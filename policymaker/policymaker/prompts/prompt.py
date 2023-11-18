from abc import ABC, abstractmethod
from typing import TypedDict


class Prompt(ABC):
    """Abstract class for prompts"""

    @abstractmethod
    def generate(self, **kwargs) -> str:
        """Generate a prompt

        Args:
            **kwargs: replacement values for the prompt

        Returns:
            The prompt
        """

        raise NotImplementedError

    @abstractmethod
    def parse_answer(self, answer: str) -> TypedDict:
        """Parse an answer

        Args:
            answer: the answer to parse

        Returns:
            The parsed answer
        """

        raise NotImplementedError
