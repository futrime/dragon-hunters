import asyncio
import logging
import os

import dotenv

from policymaker import PolicyMaker


async def main():
    dotenv.load_dotenv()

    bot_host = os.environ.get("BOT_HOST", "127.0.0.1")
    bot_port = os.environ.get("BOT_PORT", "8080")
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    openai_api_key = os.environ.get("OPENAI_API_KEY", None)
    registry_address = os.environ.get("REGISTRY_ADDRESS", None)

    setup_logging(log_level)

    logging.info("initializing...")

    if bot_port.isdigit() is False:
        raise ValueError("BOT_PORT environment variable is not a digit string")

    if openai_api_key is None:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    policy_maker = PolicyMaker(
        {
            "bot_host": bot_host,
            "bot_port": int(bot_port),
            "openai_api_key": openai_api_key,
            "registry_address": registry_address,
        }
    )

    logging.info("starting...")

    await policy_maker.start()

    # Wait for all tasks to finish.
    await asyncio.wait(asyncio.all_tasks())

    logging.info("finished")


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
