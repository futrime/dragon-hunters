import asyncio
from typing import List, TypedDict

from openai import AsyncOpenAI

from .bot import Bot


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
        self._openai_client: AsyncOpenAI = AsyncOpenAI(
            api_key=self._options["openai_api_key"]
        )
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
        """Runs the agent."""
