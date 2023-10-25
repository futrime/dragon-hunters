import copy
from typing import TypedDict

import jsonschema

from .bot_api_client import BotApiClient
from .bot_observe_response_data import (
    JSON_SCHEMA as BOT_OBSERVE_RESPONSE_DATA_JSON_SCHEMA,
)
from .bot_observe_response_data import BotObserveResponseData
from .bot_status_response_data import (
    JSON_SCHEMA as BOT_STATUS_RESPONSE_DATA_JSON_SCHEMA,
)
from .bot_status_response_data import BotStatusResponseData


class BotOptions(TypedDict):
    """Options for the bot.

    Attributes:
        host: The host to connect to.
        port: The port to connect to.
    """

    host: str
    port: int


class Bot:
    """A bot that can be run."""

    def __init__(self, options: BotOptions):
        """Initialize a bot.

        Args:
            options: The options for the bot.
        """

        self._options: BotOptions = copy.deepcopy(options)

        self._api_client: BotApiClient = BotApiClient(
            {
                "host": self._options["host"],
                "port": self._options["port"],
            }
        )
        self._is_running: bool = False

    async def start(self):
        """Starts the bot.

        Raises:
            RuntimeError: If the bot is already running.
        """

        if self._is_running:
            raise RuntimeError("bot is already running")

        self._is_running = True

    async def stop(self):
        """Stops the bot.

        Raises:
            RuntimeError: If the bot is not running.
        """

        if not self._is_running:
            raise RuntimeError("bot is not running")

        self._is_running = False

    async def get_status(self) -> BotStatusResponseData:
        """Gets the bot's status.

        Returns:
            The bot's status.

        Raises:
            BotApiError: If the bot API returns an error.
        """

        response_data = await self._api_client.get("/status")

        try:
            jsonschema.validate(
                instance=response_data, schema=BOT_STATUS_RESPONSE_DATA_JSON_SCHEMA
            )

        except jsonschema.ValidationError as e:
            raise jsonschema.ValidationError(f"invalid response from bot API: {e}")

        return BotStatusResponseData(**response_data)

    async def observe(self) -> BotObserveResponseData:
        """Observes the world

        Returns:
            The bot's observation of the world.

        Raises:
            BotApiError: If the bot API returns an error.
        """

        response_data = await self._api_client.post("/observe", {})

        try:
            jsonschema.validate(
                instance=response_data, schema=BOT_OBSERVE_RESPONSE_DATA_JSON_SCHEMA
            )

        except jsonschema.ValidationError as e:
            raise jsonschema.ValidationError(f"invalid response from bot API: {e}")

        return BotObserveResponseData(**response_data)
