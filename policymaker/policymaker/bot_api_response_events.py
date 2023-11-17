from typing import Any, Dict, TypedDict

EVENT_JSON_SCHEMA = {
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

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": EVENT_JSON_SCHEMA,
        },
    },
    "required": ["items"],
}


class EventInfo(TypedDict):
    id: str
    name: str
    description: str
    args: Dict[str, Any]
    updated: str
