import asyncio
import copy
import logging
from typing import Any, Dict, List, TypedDict
from warnings import catch_warnings

import jsonschema

from .bot_api_client import BotApiClient
from .bot_observe_response import JSON_SCHEMA as BOT_OBSERVE_RESPONSE_DATA_JSON_SCHEMA
from .bot_observe_response import BotObserveResponse
from .bot_status_response import JSON_SCHEMA as BOT_STATUS_RESPONSE_DATA_JSON_SCHEMA
from .bot_status_response import BotStatusResponse


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

    STATE_UPDATE_INTERVAL: float = 0.1

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
        self._logger = logging.getLogger("bot")
        self._tasks: List[asyncio.Task] = []

    async def create_job(self, action: str, args: Dict[str, Any]) -> str:
        """Creates a job.

        Args:
            action: The action name of the job.
            args: The arguments of the job.

        Returns:
            The ID of the created job.
        """

        # TODO: Implement this method.

        return ""

    async def observe(self) -> BotObserveResponse:
        """Observes the world

        Returns:
            The bot's observation of the world.
        """

        response_data = await self._api_client.post("/observe", {})

        try:
            jsonschema.validate(
                instance=response_data, schema=BOT_OBSERVE_RESPONSE_DATA_JSON_SCHEMA
            )

        except jsonschema.ValidationError as e:
            raise jsonschema.ValidationError(f"invalid response from bot API: {e}")

        response = BotObserveResponse(**response_data)

        return response

    async def start(self):
        """Starts the bot."""

        if self._is_running:
            raise RuntimeError("bot is already running")

        assert self._tasks.count == 0

        self._tasks.append(asyncio.create_task(self._update_status()))

        self._is_running = True

    async def stop(self):
        """Stops the bot."""

        if not self._is_running:
            raise RuntimeError("bot is not running")

        for task in self._tasks:
            task.cancel()

        self._tasks.clear()

        self._is_running = False

    async def _update_status(self):
        while True:
            await asyncio.sleep(Bot.STATE_UPDATE_INTERVAL)

            try:
                response_data = await self._api_client.get("/status")

            except Exception as e:
                self._logger.error(f"Failed to update status: {e}")
                continue

            try:
                jsonschema.validate(
                    instance=response_data, schema=BOT_STATUS_RESPONSE_DATA_JSON_SCHEMA
                )

            except jsonschema.ValidationError as e:
                raise jsonschema.ValidationError(f"invalid response from bot API: {e}")
