import asyncio
import logging
import os
from typing import Any, Tuple

import aiohttp
import dotenv
import jsonschema

from policymaker import PolicyMaker

API_VERSION = "0.0.0"
REGISTRY_POLICYMAKERS_POST_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "bot": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "ip": {"type": "string"},
                "port": {"type": "integer"},
            },
        },
        "ip": {"type": "string"},
        "port": {"type": "integer"},
    },
}


async def main():
    dotenv.load_dotenv()

    bot_host = os.environ.get("BOT_HOST", "127.0.0.1")
    bot_port_str = os.environ.get("BOT_PORT", "8080")
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    openai_api_key = os.environ.get("OPENAI_API_KEY", None)
    registry_address = os.environ.get("REGISTRY_ADDRESS", None)

    if registry_address is not None:
        logging.info("getting bot host and port from registry...")
        bot_host, bot_port = await get_from_registry(registry_address)
        logging.info(f"got bot at {bot_host}")

    setup_logging(log_level)

    if openai_api_key is None:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    logging.info("starting...")

    # Check if the port is a valid integer
    try:
        bot_port = int(bot_port_str)

    except ValueError:
        raise ValueError(f"invalid bot port: {bot_port_str}")

    policy_maker = PolicyMaker(
        {
            "bot_host": bot_host,
            "bot_port": bot_port,
            "openai_api_key": openai_api_key,
        }
    )

    await policy_maker.start()

    # Wait for all tasks to finish.
    await asyncio.wait(asyncio.all_tasks())


async def get_from_registry(registry_address: str) -> Tuple[str, int]:
    """Get the bot host and port from the registry.

    Args:
        registry_address: The address of the registry.

    Returns:
        A tuple of the bot host and port.
    """

    response_data: Any = None

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{registry_address}/api/policymakers",
                json={
                    "apiVersion": API_VERSION,
                    "data": {},
                },
            ) as response:
                response_data = await response.json()
    except Exception as e:
        raise RuntimeError(f"error while getting from registry: {e}")

    # Validate the response format.
    try:
        jsonschema.validate(
            instance=response_data, schema=REGISTRY_POLICYMAKERS_POST_RESPONSE_SCHEMA
        )
    except jsonschema.ValidationError as e:
        raise jsonschema.ValidationError(f"invalid response from registry: {e}")

    # If the API returned an error, raise a RuntimeError.
    if "error" in response_data:
        raise RuntimeError(
            f"error from registry API: {response_data['error']['message']}"
        )
    else:
        return (
            response_data["data"]["bot"]["ip"],
            response_data["data"]["bot"]["port"],
        )


def setup_logging(logging_level_str: str):
    """Setup the logging.

    Args:
        logging_level_str: The logging level as a string.
    """

    if logging_level_str == "DEBUG":
        log_level = logging.DEBUG
    elif logging_level_str == "INFO":
        log_level = logging.INFO
    elif logging_level_str == "WARNING":
        log_level = logging.WARNING
    elif logging_level_str == "ERROR":
        log_level = logging.ERROR
    elif logging_level_str == "CRITICAL":
        log_level = logging.CRITICAL
    else:
        raise ValueError(f"invalid logging level: {logging_level_str}")

    logging.basicConfig(level=log_level)


if __name__ == "__main__":
    asyncio.run(main())
