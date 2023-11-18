from typing import Dict

from .event_data import EventData
from .response import Response


class GetEventsResponse(Response):
    def __init__(self, data: Dict):
        super().__init__(data, _JSON_SCHEMA)

    def data(self) -> Dict[str, EventData]:
        """Return the response data.

        Returns:
            Dict[str, EventData]: A map from event ids to EventData objects.
        """

        return {
            event["id"]: EventData(
                {
                    "id": event["id"],
                    "name": event["name"],
                    "description": event["description"],
                    "args": {arg["name"]: arg["value"] for arg in event["args"]},
                    "updated": event["updated"],
                }
            )
            for event in self._data["items"]
        }


_EVENT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "args": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "value": {},
                },
                "required": ["name", "value"],
            },
        },
        "updated": {"type": "string"},
    },
    "required": ["id", "name", "description", "args", "updated"],
}

_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": _EVENT_JSON_SCHEMA,
        },
    },
    "required": ["items"],
}
