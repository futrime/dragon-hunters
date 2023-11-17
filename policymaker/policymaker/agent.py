import asyncio
import logging
from typing import List, TypedDict

from .bot import Bot
from .gpt35turbo_wrapper import GPT35TurboWrapper


class AgentOptions(TypedDict):
    """Options for the language model agent.

    Attributes:
        openai_api_key: The OpenAI API key.
    """

    openai_api_key: str


class Agent:
    def __init__(self, options: AgentOptions, bot: Bot):
        self._options: AgentOptions = options

        self._bot: Bot = bot
        self._is_running: bool = False
        self._logger = logging.getLogger("agent")
        self._model = GPT35TurboWrapper(options["openai_api_key"])
        self._tasks: List[asyncio.Task] = []

    async def start(self):
        """Starts the agent."""

        if self._is_running:
            raise RuntimeError("bot is already running")

        assert len(self._tasks) == 0

        self._tasks.append(asyncio.create_task(self._run()))

    async def stop(self):
        """Stops the agent."""

        if not self._is_running:
            raise RuntimeError("bot is not running")

        for task in self._tasks:
            task.cancel()

        self._tasks.clear()

        self._is_running = False

    async def _run(self):
        while True:
            await asyncio.sleep(1)

            answer = await self._model.ask("Hello, how are you?")

            self._logger.info(answer)
