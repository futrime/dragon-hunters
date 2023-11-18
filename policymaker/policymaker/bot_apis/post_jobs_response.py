from typing import Dict

from .job_data import JobData
from .response import Response


class PostJobsResponse(Response):
    def __init__(self, data: Dict):
        super().__init__(data, _JSON_SCHEMA)

    def data(self) -> JobData:
        return JobData(
            {
                "id": self._data["id"],
                "action": self._data["action"],
                "args": {arg["name"]: arg["value"] for arg in self._data["args"]},
                "state": self._data["state"],
                "message": self._data["message"],
            }
        )


_JSON_SCHEMA = {
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
