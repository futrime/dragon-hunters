import asyncio
import logging
import os

import dotenv

from policymaker import PolicyMaker


async def main():
    try:
        dotenv.load_dotenv()

        setup_logging()

        logging.info("starting...")

        bot_host = os.environ.get("BOT_HOST", "127.0.0.1")
        bot_port_str = os.environ.get("BOT_PORT", "8080")
        openai_api_key = os.environ.get("OPENAI_API_KEY", "")

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

        await policy_maker.run()

    except Exception as e:
        logging.exception(e)


def setup_logging():
    logging_level_str = os.environ.get("LOGGING_LEVEL", "INFO")

    if logging_level_str == "DEBUG":
        logging_level = logging.DEBUG
    elif logging_level_str == "INFO":
        logging_level = logging.INFO
    elif logging_level_str == "WARNING":
        logging_level = logging.WARNING
    elif logging_level_str == "ERROR":
        logging_level = logging.ERROR
    elif logging_level_str == "CRITICAL":
        logging_level = logging.CRITICAL
    else:
        raise ValueError(f"invalid logging level: {logging_level_str}")

    logging.basicConfig(level=logging_level)


if __name__ == "__main__":
    asyncio.run(main())
