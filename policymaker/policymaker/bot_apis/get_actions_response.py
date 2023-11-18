from typing import Dict

from .action_data import ActionData
from .response import Response


class GetActionsResponse(Response):
    def __init__(self, data: Dict):
        super().__init__(data, _JSON_SCHEMA)

    def data(self) -> Dict[str, ActionData]:
        """Return the response data.

        Returns:
            Dict[str, ActionData]: A map from action names to ActionData objects.
        """

        return {
            action["name"]: ActionData(
                {
                    "name": action["name"],
                    "description": action["description"],
                    "parameters": {
                        parameter["name"]: {
                            "name": parameter["name"],
                            "description": parameter["description"],
                            "type": parameter["type"],
                        }
                        for parameter in action["parameters"]
                    },
                }
            )
            for action in self._data["items"]
        }


_ACTION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "parameters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "type": {"type": "string"},
                },
                "required": ["name", "description", "type"],
            },
        },
    },
    "required": ["name", "description", "parameters"],
}

_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": _ACTION_JSON_SCHEMA,
        },
    },
    "required": ["items"],
}
