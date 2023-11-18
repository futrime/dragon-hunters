from typing import Dict

from .action_data import ActionData
from .response import Response


class PostActionsResponse(Response):
    def __init__(self, data: Dict):
        super().__init__(data, _JSON_SCHEMA)

    def data(self) -> ActionData:
        return ActionData(
            {
                "name": self._data["name"],
                "description": self._data["description"],
                "parameters": {
                    parameter["name"]: {
                        "name": parameter["name"],
                        "description": parameter["description"],
                        "type": parameter["type"],
                    }
                    for parameter in self._data["parameters"]
                },
            }
        )


_JSON_SCHEMA = {
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
