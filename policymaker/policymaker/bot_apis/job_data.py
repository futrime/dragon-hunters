from typing import Any, Dict, TypedDict


class JobData(TypedDict):
    id: str
    action: str
    args: Dict[str, Any]
    state: str
    message: str
