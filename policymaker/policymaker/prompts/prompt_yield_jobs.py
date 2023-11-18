from typing import Any, Dict, TypedDict

from .prompt import Prompt


class PromptYieldJobs(Prompt):
    """Prompt for yielding jobs"""

    PROMPT_TEMPLATE = """
You are a senior Minecraft player. Now you are playing Minecraft controlling a player. \
The observed environment and player information is presented below. \
You can use the information to make decisions.
<information>
{game_info}
</information>
"""

    async def generate(self, **kwargs) -> str:
        return PromptYieldJobs.PROMPT_TEMPLATE.format(game_info=kwargs["game_info"])

    async def parse_answer(self, answer: str) -> TypedDict:
        return Answer()


class Answer(TypedDict):
    """Answer to the prompt"""

    pass
