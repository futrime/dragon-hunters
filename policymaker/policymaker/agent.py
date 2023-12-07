import asyncio
import logging
from typing import Any, Dict, List, Optional, TypedDict

from policymaker.bot_apis.observation_data import ObservationData

from .bot import Bot
from .models.gpt35turbo_wrapper import GPT35TurboWrapper
from .prompts.prompt_yield_jobs import PromptYieldJobs


class AgentOptions(TypedDict):
    """Options for the language model agent.

    Attributes:
        openai_api_key: The OpenAI API key.
    """

    openai_api_key: str


class Agent:
    def __init__(self, options: AgentOptions, bot: Bot):
        self._options: AgentOptions = options

        self._bot: Bot = bot
        self._is_running: bool = False
        self._logger = logging.getLogger("agent")
        self._model = GPT35TurboWrapper(options["openai_api_key"])
        self._tasks: List[asyncio.Task] = []

        # Logic related stuff
        self._observation_data: Optional[ObservationData] = None
        self._prompt_yield_jobs = PromptYieldJobs()

    async def start(self):
        """Starts the agent."""

        if self._is_running:
            raise RuntimeError("bot is already running")

        assert len(self._tasks) == 0

        self._tasks.append(asyncio.create_task(self._run()))

    async def stop(self):
        """Stops the agent."""

        if not self._is_running:
            raise RuntimeError("bot is not running")

        for task in self._tasks:
            task.cancel()

        self._tasks.clear()

        self._is_running = False

    def _generate_prompt(self) -> str:
        if self._observation_data is None:
            raise RuntimeError("observation data is not available")

        # TODO: Generate the prompt.

        return self._prompt_yield_jobs.generate(
            game_info=str(self._observation_data["blocksNearby"])
        )

    async def _perform_action(self, action: str, args: Dict[str, Any]):
        job_id = await self._bot.create_job(action, args)

        await self._bot.start_job(job_id)

        while True:
            await asyncio.sleep(0)

            job_data = await self._bot.get_jobs()

            for job_id in job_data:
                job = job_data[job_id]
                if job["id"] != job_id:
                    continue

                if job["state"] == "CANCELED" or job["state"] == "SUCCEEDED":
                    break

                elif job["state"] == "FAILED":
                    raise RuntimeError(f"job {job_id} failed: {job['message']}")

    async def _run(self):
        prompt_yield_jobs = PromptYieldJobs()

        while True:
            try:
                await asyncio.sleep(1)

                self._observation_data = await self._bot.observe()

                prompt = self._generate_prompt()

                # Ask the model for the answer.
                ans_str = await self._model.ask(prompt)

                self._logger.info(f"{ans_str}")

                ans = prompt_yield_jobs.parse_answer(ans_str)

                for item in ans["items"]:
                    await self._perform_action(item["action"], item["args"])

            except Exception as e:
                self._logger.error(f"an error occurred while running the agent: {e}")
