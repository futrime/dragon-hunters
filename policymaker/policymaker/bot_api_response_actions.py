from typing import Dict, TypedDict

ACTION_JSON_SCHEMA = {
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

POST_JSON_SCHEMA = ACTION_JSON_SCHEMA

GET_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": ACTION_JSON_SCHEMA,
        },
    },
}


class ParameterInfo(TypedDict):
    name: str
    description: str
    type: str


class ActionInfo(TypedDict):
    name: str
    description: str
    parameters: Dict[str, ParameterInfo]
