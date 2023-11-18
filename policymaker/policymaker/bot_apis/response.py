from abc import ABC, abstractmethod
from typing import Any, Dict

import jsonschema


class Response(ABC):
    """Abstract base class for all responses from the bot API."""

    def __init__(self, data: Dict, json_schema: Dict):
        # Validate the response format.
        try:
            jsonschema.validate(instance=data, schema=json_schema)

        except jsonschema.ValidationError as e:
            raise jsonschema.ValidationError(f"invalid response data: {e}")

        self._data = data

    @abstractmethod
    def data(self) -> Any:
        """Return the response data."""

        pass
