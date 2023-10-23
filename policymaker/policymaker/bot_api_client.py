from typing import Any, Dict, TypedDict

import aiohttp
import jsonschema

_DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "apiVersion": {
            "type": "string",
        },
        "data": {
            "type": "object",
        },
    },
    "required": ["apiVersion", "data"],
}

_ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "apiVersion": {
            "type": "string",
        },
        "error": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "integer",
                },
                "message": {
                    "type": "string",
                },
            },
            "required": ["code", "message"],
        },
    },
    "required": ["apiVersion", "error"],
}

_GENERAL_SCHEMA = {
    "oneOf": [
        _DATA_SCHEMA,
        _ERROR_SCHEMA,
    ],
}


class BotApiClientOptions(TypedDict):
    """Options for the bot API client.

    Attributes:
        host: The host to connect to.
        port: The port to connect to.
    """

    host: str
    port: int


class BotApiClient:
    """A client for the bot API."""

    def __init__(self, options: BotApiClientOptions):
        """Initialize a bot API client.

        Args:
            options: The options for the bot API client.
        """

        self._options: BotApiClientOptions = options

    async def get(self, path: str) -> Dict[str, Any]:
        """Gets a resource from the bot API.

        Args:
            path: The path to the resource.

        Returns:
            The resource.
        """

        # Prepend a slash to the path if it doesn't already have one.
        if not path.startswith("/"):
            path = f"/{path}"

        response_data: Any = None
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://{self._options['host']}:{self._options['port']}{path}"
            ) as response:
                response_data = await response.json()

        try:
            jsonschema.validate(instance=response_data, schema=_GENERAL_SCHEMA)
        except jsonschema.ValidationError:
            raise RuntimeError("invalid response from bot API")

        if "error" in response_data:
            raise RuntimeError(
                f"error from bot API: {response_data['error']['message']}"
            )

        else:
            return response_data["data"]

    async def post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Posts data to the bot API.

        Args:
            path: The path to the resource.
            data: The data to post.

        Returns:
            The response.
        """

        # Prepend a slash to the path if it doesn't already have one.
        if not path.startswith("/"):
            path = f"/{path}"

        response_data: Any = None
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{self._options['host']}:{self._options['port']}{path}",
                json=data,
            ) as response:
                response_data = await response.json()

        try:
            jsonschema.validate(instance=response_data, schema=_GENERAL_SCHEMA)
        except jsonschema.ValidationError:
            raise RuntimeError("invalid response from bot API")

        if "error" in response_data:
            raise RuntimeError(
                f"error from bot API: {response_data['error']['message']}"
            )

        else:
            return response_data["data"]
