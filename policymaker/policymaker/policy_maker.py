import copy
import logging
from typing import TypedDict

from .agent import Agent
from .bot import Bot


class PolicyMakerOptions(TypedDict):
    """Options for the policy maker.

    Attributes:
        bot_host: The host of the bot.
        bot_port: The port of the bot.
        openai_api_key: The OpenAI API key.
    """

    bot_host: str
    bot_port: int
    openai_api_key: str


class PolicyMaker:
    def __init__(self, options: PolicyMakerOptions):
        self._options: PolicyMakerOptions = copy.deepcopy(options)

        self._logger = logging.getLogger("policymaker")

        self._bot: Bot = Bot(
            {
                "host": self._options["bot_host"],
                "port": self._options["bot_port"],
            }
        )

        self._agent: Agent = Agent(
            {
                "openai_api_key": self._options["openai_api_key"],
            },
            self._bot,
        )

    async def start(self):
        """Starts the policy maker."""

        await self._bot.start()

        await self._agent.start()

    async def stop(self):
        """Stops the policy maker."""

        await self._agent.stop()

        await self._bot.stop()
