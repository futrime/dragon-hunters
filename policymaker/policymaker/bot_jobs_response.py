from typing import Any, Dict, TypedDict

JOB_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
        },
        "action": {
            "type": "string",
        },
        "args": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                    },
                    "value": {},
                },
                "required": ["name", "value"],
            },
        },
        "state": {
            "type": "string",
        },
        "message": {
            "type": "string",
        },
    },
    "required": ["id", "action", "args", "state", "message"],
}

POST_JSON_SCHEMA = JOB_JSON_SCHEMA

GET_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": JOB_JSON_SCHEMA,
        },
    },
}


class JobInfo(TypedDict):
    id: str
    action: str
    args: Dict[str, Any]
    state: str
    message: str
