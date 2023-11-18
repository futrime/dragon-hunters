from typing import Dict

from .job_data import JobData
from .response import Response


class GetJobsResponse(Response):
    def __init__(self, data: Dict):
        super().__init__(data, _JSON_SCHEMA)

    def data(self) -> Dict[str, JobData]:
        return {
            job["id"]: JobData(
                {
                    "id": job["id"],
                    "action": job["action"],
                    "args": {arg["name"]: arg["value"] for arg in job["args"]},
                    "state": job["state"],
                    "message": job["message"],
                }
            )
            for job in self._data["items"]
        }


_JOB_JSON_SCHEMA = {
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

_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": _JOB_JSON_SCHEMA,
        },
    },
    "required": ["items"],
}
