from abc import ABC, abstractmethod


class Prompt(ABC):
    """Abstract class for prompts"""

    @abstractmethod
    async def generate(self, **kwargs) -> str:
        """Generate a prompt

        Args:
            **kwargs: replacement values for the prompt

        Returns:
            The prompt
        """

        raise NotImplementedError
