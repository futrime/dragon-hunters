from abc import ABC, abstractmethod
from typing import Dict, TypedDict

import jsonschema


class Response(ABC):
    """Abstract base class for all responses from the bot API."""

    def __init__(self, data: Dict, json_schema: Dict):
        """Initialize the response.

        Args:
            data: the response data
            json_schema: the JSON schema for validating the response data
        """

        # Validate the response format.
        try:
            jsonschema.validate(instance=data, schema=json_schema)

        except jsonschema.ValidationError as e:
            raise jsonschema.ValidationError(f"invalid response data: {e}")

        self._data = data

    @abstractmethod
    def data(self) -> TypedDict:
        """Return the response data.

        Returns:
            The response data
        """

        raise NotImplementedError
