import copy
from typing import TypedDict

from .legacy_framework.agent import Agent
from .legacy_framework.bot_connection import BotConnection


class PolicyMakerOptions(TypedDict):
    bot_host: str
    bot_port: int
    openai_api_key: str


class PolicyMaker:
    def __init__(self, options: PolicyMakerOptions):
        self._options: PolicyMakerOptions = copy.deepcopy(options)

    async def run(self):
        connection = BotConnection()
        agent = Agent(connection)

        agent.run()
