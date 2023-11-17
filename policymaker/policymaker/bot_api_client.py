import urllib.parse
from typing import Any, Dict, TypedDict

import aiohttp
import jsonschema

from .bot_api_error import BotApiError

_API_VERSION = "0.0.0"

_DATA_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "apiVersion": {
            "type": "string",
            "const": _API_VERSION,
        },
        "data": {
            "type": "object",
        },
    },
    "required": ["apiVersion", "data"],
}

_ERROR_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "apiVersion": {
            "type": "string",
            "const": _API_VERSION,
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

    async def get(self, path: str, queries: Dict[str, str] = {}) -> Dict[str, Any]:
        """Gets a resource from the bot API.

        Args:
            path: The path to the resource.

        Returns:
            The resource.
        """

        # Prepend a slash to the path if it doesn't already have one.
        if not path.startswith("/"):
            path = f"/{path}"

        # URL encode the queries.
        queries = {
            k: urllib.parse.quote(v) for k, v in queries.items() if v is not None
        }

        response_data: Any = None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://{self._options['host']}:{self._options['port']}/api{path}",
                    params=queries,
                ) as response:
                    response_data = await response.json()
        except Exception as e:
            raise RuntimeError(f"error while getting from bot API: {e}")

        # Validate the response format.
        try:
            jsonschema.validate(instance=response_data, schema=_GENERAL_SCHEMA)
        except jsonschema.ValidationError as e:
            raise jsonschema.ValidationError(f"invalid response from bot API: {e}")

        # If the API returned an error, raise a BotApiError.
        if "error" in response_data:
            raise BotApiError(
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

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{self._options['host']}:{self._options['port']}/api{path}",
                    json={
                        "apiVersion": _API_VERSION,
                        "data": data,
                    },
                ) as response:
                    response_data = await response.json()
        except Exception as e:
            raise RuntimeError(f"error while posting to bot API: {e}")

        # Validate the response format.
        try:
            jsonschema.validate(instance=response_data, schema=_GENERAL_SCHEMA)
        except jsonschema.ValidationError as e:
            raise jsonschema.ValidationError(f"invalid response from bot API: {e}")

        # If the API returned an error, raise a BotApiError.
        if "error" in response_data:
            raise BotApiError(
                f"error from bot API: {response_data['error']['message']}"
            )
        else:
            return response_data["data"]
