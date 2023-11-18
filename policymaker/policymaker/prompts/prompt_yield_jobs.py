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

    async def generate(self, game_info: str) -> str:
        """Generate a prompt

        Args:
            **kwargs: replacement values for the prompt

        Returns:
            The prompt
        """

        return PromptYieldJobs.PROMPT_TEMPLATE.format(game_info=game_info)