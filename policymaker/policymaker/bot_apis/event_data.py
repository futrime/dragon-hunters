from typing import Any, Dict, TypedDict


class EventData(TypedDict):
    id: str
    name: str
    description: str
    args: Dict[str, Any]
    updated: str
