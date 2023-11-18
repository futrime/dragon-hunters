from typing import Dict, TypedDict


class Parameter(TypedDict):
    name: str
    description: str
    type: str


class ActionData(TypedDict):
    name: str
    description: str
    parameters: Dict[str, Parameter]
