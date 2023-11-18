from abc import ABC, abstractmethod


class ModelWrapper(ABC):
    """Abstract class for model wrappers"""

    @abstractmethod
    async def ask(self, message: str) -> str:
        """Send a message to the model and wait for a response

        Args:
            message: The message to send to the model

        Returns:
            The response from the model
        """

        raise NotImplementedError
