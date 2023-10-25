class BotApiError(Exception):
    """An error from the bot API."""

    def __init__(self, message: str):
        """Initialize a BotApiError.

        Args:
            message: The message for the error.
        """

        super().__init__(message)
