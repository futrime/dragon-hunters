import asyncio
import copy
import logging
from typing import Any, Dict, List, TypedDict

import jsonschema

from .bot_api_client import BotApiClient
from .bot_jobs_response import GET_JSON_SCHEMA as BOT_JOBS_GET_RESPONSE_DATA_JSON_SCHEMA
from .bot_jobs_response import (
    POST_JSON_SCHEMA as BOT_JOBS_POST_RESPONSE_DATA_JSON_SCHEMA,
)
from .bot_jobs_response import JobInfo
from .bot_observe_response import JSON_SCHEMA as BOT_OBSERVE_RESPONSE_DATA_JSON_SCHEMA
from .bot_observe_response import BotInfo
from .bot_status_response import JSON_SCHEMA as BOT_STATUS_RESPONSE_DATA_JSON_SCHEMA


class BotOptions(TypedDict):
    """Options for the bot.

    Attributes:
        host: The host to connect to.
        port: The port to connect to.
    """

    host: str
    port: int


class Bot:
    """A bot that can be run."""

    STATE_UPDATE_INTERVAL: float = 0.1

    def __init__(self, options: BotOptions):
        """Initialize a bot.

        Args:
            options: The options for the bot.
        """

        self._options: BotOptions = copy.deepcopy(options)

        self._api_client: BotApiClient = BotApiClient(
            {
                "host": self._options["host"],
                "port": self._options["port"],
            }
        )
        self._is_running: bool = False
        self._logger = logging.getLogger("bot")
        self._tasks: List[asyncio.Task] = []

    async def start(self):
        """Starts the bot."""

        if self._is_running:
            raise RuntimeError("bot is already running")

        assert len(self._tasks) == 0

        self._tasks.append(asyncio.create_task(self._update_status()))

        self._is_running = True

    async def stop(self):
        """Stops the bot."""

        if not self._is_running:
            raise RuntimeError("bot is not running")

        for task in self._tasks:
            task.cancel()

        self._tasks.clear()

        self._is_running = False

    async def observe(self) -> BotInfo:
        """Observes the world

        Returns:
            The bot's observation of the world.
        """

        response_data = await self._api_client.post("/observe", {})

        jsonschema.validate(
            instance=response_data, schema=BOT_OBSERVE_RESPONSE_DATA_JSON_SCHEMA
        )

        response = BotInfo(response_data["bot"])

        return response

    async def create_job(self, action: str, args: Dict[str, Any]) -> str:
        """Creates a job.

        Args:
            action: The action name of the job.
            args: The arguments of the job.

        Returns:
            The ID of the created job.
        """

        response_data = await self._api_client.post(
            "/jobs",
            {
                "action": action,
                "args": [
                    {
                        "name": name,
                        "value": value,
                    }
                    for name, value in args.items()
                ],
            },
        )

        jsonschema.validate(
            instance=response_data, schema=BOT_JOBS_POST_RESPONSE_DATA_JSON_SCHEMA
        )

        return response_data["id"]

    async def get_jobs(self) -> Dict[str, JobInfo]:
        """Gets all jobs.

        Returns:
            The jobs.
        """

        response_data = await self._api_client.get("/jobs")

        jsonschema.validate(
            instance=response_data, schema=BOT_JOBS_GET_RESPONSE_DATA_JSON_SCHEMA
        )

        # No duplicate IDs
        assert len({job["id"] for job in response_data["items"]}) == len(
            response_data["items"]
        )

        # No duplicate argument name of each job
        for job in response_data["items"]:
            assert len({arg["name"] for arg in job["args"]}) == len(job["args"])

        return {
            job["id"]: JobInfo(
                {
                    "id": job["id"],
                    "action": job["action"],
                    "args": {arg["name"]: arg["value"] for arg in job["args"]},
                    "state": job["state"],
                    "message": job["message"],
                }
            )
            for job in response_data["items"]
        }

    async def start_job(self, job: str):
        """Starts a job.

        Args:
            job: The ID of the job to start.
        """

        await self._api_client.post(f"/jobs/{job}/start", {})

    async def pause_job(self, job: str):
        """Pauses a job.

        Args:
            job: The ID of the job to pause.
        """

        await self._api_client.post(f"/jobs/{job}/pause", {})

    async def resume_job(self, job: str):
        """Resumes a job.

        Args:
            job: The ID of the job to resume.
        """

        await self._api_client.post(f"/jobs/{job}/resume", {})

    async def cancel_job(self, job: str):
        """Cancels a job.

        Args:
            job: The ID of the job to cancel.
        """

        await self._api_client.post(f"/jobs/{job}/cancel", {})

    async def _update_status(self):
        while True:
            await asyncio.sleep(Bot.STATE_UPDATE_INTERVAL)

            try:
                response_data = await self._api_client.get("/status")

            except Exception as e:
                self._logger.error(f"Failed to update status: {e}")
                continue

            try:
                jsonschema.validate(
                    instance=response_data, schema=BOT_STATUS_RESPONSE_DATA_JSON_SCHEMA
                )

            except jsonschema.ValidationError as e:
                raise jsonschema.ValidationError(f"invalid response from bot API: {e}")
