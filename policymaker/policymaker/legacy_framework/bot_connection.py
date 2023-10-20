import aiohttp

from .connection import Connection


class BotConnection(Connection):
    def start_env(self) -> bool:
        return True

    def step_env(self, command: str) -> None:
        # TODO: implement
        pass

    def observe_env(self) -> dict:
        return {}
