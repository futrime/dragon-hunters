from __future__ import annotations

import asyncio
import copy
from typing import TypedDict


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

        self._loop_task: asyncio.Task[None] | None = None

    async def run(self):
        """Runs the bot.

        Raises:
            RuntimeError: If the bot is already running.
        """

        if self._loop_task is not None:
            raise RuntimeError("bot is already running")

        self._loop_task = asyncio.create_task(self._loop())

    async def stop(self):
        """Stops the bot.

        Raises:
            RuntimeError: If the bot is not running.
        """

        if self._loop_task is None:
            raise RuntimeError("bot is not running")

        self._loop_task.cancel("bot is stopping")
        await self._loop_task

    async def _loop(self) -> None:
        while True:
            pass
