import asyncio
import copy
import logging
from typing import Any, Optional, Tuple, TypedDict

import aiohttp
import jsonschema

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
    registry_address: Optional[str]


class PolicyMaker:
    def __init__(self, options: PolicyMakerOptions):
        self._options: PolicyMakerOptions = copy.deepcopy(options)

        self._logger = logging.getLogger("policymaker")

        if options["registry_address"] is not None:
            self._logger.info("getting bot host and port from registry...")
            (
                self._options["bot_host"],
                self._options["bot_port"],
            ) = asyncio.get_event_loop().run_until_complete(
                PolicyMaker._get_from_registry(options["registry_address"])
            )
            self._logger.info(
                f"got bot at {self._options['bot_host']}:{self._options['bot_port']}"
            )

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

    _API_VERSION = "0.0.0"
    _REGISTRY_POLICYMAKERS_POST_RESPONSE_SCHEMA = {
        "type": "object",
        "properties": {
            "bot": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "ip": {"type": "string"},
                    "port": {"type": "integer"},
                },
            },
            "ip": {"type": "string"},
            "port": {"type": "integer"},
        },
    }

    @staticmethod
    async def _get_from_registry(registry_address: str) -> Tuple[str, int]:
        """Get the bot host and port from the registry.

        Args:
            registry_address: The address of the registry.

        Returns:
            A tuple of the bot host and port.
        """

        response_data: Any = None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{registry_address}/api/policymakers",
                    json={
                        "apiVersion": PolicyMaker._API_VERSION,
                        "data": {},
                    },
                ) as response:
                    response_data = await response.json()
        except Exception as e:
            raise RuntimeError(f"error while getting from registry: {e}")

        # Validate the response format.
        try:
            jsonschema.validate(
                instance=response_data,
                schema=PolicyMaker._REGISTRY_POLICYMAKERS_POST_RESPONSE_SCHEMA,
            )
        except jsonschema.ValidationError as e:
            raise jsonschema.ValidationError(f"invalid response from registry: {e}")

        # If the API returned an error, raise a RuntimeError.
        if "error" in response_data:
            raise RuntimeError(
                f"error from registry API: {response_data['error']['message']}"
            )
        else:
            return (
                response_data["data"]["bot"]["ip"],
                response_data["data"]["bot"]["port"],
            )
