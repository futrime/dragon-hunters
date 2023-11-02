import copy
import logging
from typing import TypedDict

from .bot import Bot


class PolicyMakerOptions(TypedDict):
    bot_host: str
    bot_port: int
    openai_api_key: str


class PolicyMaker:
    def __init__(self, options: PolicyMakerOptions):
        self._options: PolicyMakerOptions = copy.deepcopy(options)

        self._bot: Bot = Bot(
            {
                "host": self._options["bot_host"],
                "port": self._options["bot_port"],
            }
        )
        self._logger = logging.getLogger("policymaker")

    async def run(self):
        await self._bot.start()

        # TODO: Implement the policy maker.

        await self._bot.stop()
