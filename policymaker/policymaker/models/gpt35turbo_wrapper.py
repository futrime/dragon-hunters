from openai import AsyncOpenAI

from .model_wrapper import ModelWrapper


class GPT35TurboWrapper(ModelWrapper):
    """Wrapper for the gpt-3.5-turbo model"""

    def __init__(self, openai_api_key: str):
        self._openai_client: AsyncOpenAI = AsyncOpenAI(
            api_key=openai_api_key,
        )

    async def ask(self, message: str) -> str:
        chat_completion = await self._openai_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            model="gpt-3.5-turbo",
        )

        answer = chat_completion.choices[0].message.content

        if answer is None:
            raise ValueError("No answer from the model")

        return answer
