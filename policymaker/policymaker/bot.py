import copy
from typing import TypedDict

from .bot_api_client import BotApiClient
from .bot_observe_response_data import BotObserveResponseData


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

    async def observe(self) -> BotObserveResponseData:
        """Observes the world"""

        response_data = await self._api_client.post("/observe", {})
        return BotObserveResponseData(**response_data)

    async def run(self):
        """Runs the bot.

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
