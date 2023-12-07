import json
from typing import Any, Dict, List, TypedDict

import jsonschema

from .prompt import Prompt


class AnswerItem(TypedDict):
    """Item in the answer"""

    action: str
    args: Dict[str, Any]


class Answer(TypedDict):
    """Answer to the prompt"""

    items: List[AnswerItem]


class PromptYieldJobs(Prompt):
    """Prompt for yielding jobs"""

    PROMPT_TEMPLATE = """
You are a senior Minecraft player. Now you are playing Minecraft controlling a player. \
The observed environment and player information is presented below. \
You can use the information to make decisions. You should also follow the JSON schema.
<information>
{game_info}
</information>
<schema>
{{
    "type": "array",
    "items": {{
        "type": "object",
        "properties": {{
            "action": {{"type": "string"}},
            "args": {{"type": "object"}},
        }},
        "required": ["action", "args"],
    }},
}}
</schema>
Example answer:
'''
[
    {{"action": "ExploreUntil", "args": {{"x": 1, "y": 0, "z": 0}}}},
    {{"action": "ExploreUntil", "args": {{"x": 0, "y": 0, "z": 1}}}}
]
'''
"""

    def generate(self, game_info: str) -> str:
        return PromptYieldJobs.PROMPT_TEMPLATE.format(game_info=game_info)

    def parse_answer(self, answer: str) -> Answer:
        # Try to parse answer as JSON.
        try:
            data = json.loads(answer)

        except json.JSONDecodeError:
            raise ValueError("failed to parse answer as JSON")

        # Validate the response format.
        try:
            jsonschema.validate(instance=data, schema=_JSON_SCHEMA)

        except jsonschema.ValidationError as e:
            raise jsonschema.ValidationError(f"invalid answer format: {e}")

        return Answer(
            {
                "items": [
                    AnswerItem({"action": item["action"], "args": item["args"]})
                    for item in data
                ]
            }
        )


_JSON_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "action": {"type": "string"},
            "args": {"type": "object"},
        },
        "required": ["action", "args"],
    },
}
