import asyncio
import copy
import logging
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, List, TypedDict

import jsonschema

from .bot_api_client import BotApiClient
from .bot_api_response_actions import (
    GET_JSON_SCHEMA as BOT_ACTIONS_GET_RESPONSE_DATA_JSON_SCHEMA,
)
from .bot_api_response_actions import (
    POST_JSON_SCHEMA as BOT_ACTIONS_POST_RESPONSE_DATA_JSON_SCHEMA,
)
from .bot_api_response_actions import ActionInfo
from .bot_api_response_events import JSON_SCHEMA as BOT_EVENTS_RESPONSE_DATA_JSON_SCHEMA
from .bot_api_response_events import EventInfo
from .bot_api_response_jobs import (
    GET_JSON_SCHEMA as BOT_JOBS_GET_RESPONSE_DATA_JSON_SCHEMA,
)
from .bot_api_response_jobs import (
    POST_JSON_SCHEMA as BOT_JOBS_POST_RESPONSE_DATA_JSON_SCHEMA,
)
from .bot_api_response_jobs import JobInfo
from .bot_api_response_observe import (
    JSON_SCHEMA as BOT_OBSERVE_RESPONSE_DATA_JSON_SCHEMA,
)
from .bot_api_response_observe import BotInfo
from .bot_api_response_status import JSON_SCHEMA as BOT_STATUS_RESPONSE_DATA_JSON_SCHEMA


class ActionCreationParameter(TypedDict):
    """A parameter of creating an action.

    Attributes:
        name: The name of the parameter.
        description: The description of the parameter.
        type: The type of the parameter.
        variable: The variable to be replaced with the value of the parameter. Should start with "$".
    """

    name: str
    type: str
    description: str
    variable: str


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

    BOT_NOT_RUNNING_ERROR_MESSAGE: str = "bot is not running"
    UPDAVE_EVENTS_INTERVAL: float = 0.1
    UPDATE_STATUS_INTERVAL: float = 0.1

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
        self._event_handlers: Dict[
            str, List[Callable[[EventInfo], Coroutine[Any, Any, None]]]
        ] = {}
        self._is_running: bool = False
        self._logger = logging.getLogger("bot")
        self._tasks: List[asyncio.Task] = []

    async def start(self):
        """Starts the bot."""

        if self._is_running:
            raise RuntimeError("bot is already running")

        assert len(self._tasks) == 0

        self._tasks.append(asyncio.create_task(self._update_events()))
        self._tasks.append(asyncio.create_task(self._update_status()))

        self._is_running = True

    async def stop(self):
        """Stops the bot."""

        if not self._is_running:
            raise RuntimeError(Bot.BOT_NOT_RUNNING_ERROR_MESSAGE)

        for task in self._tasks:
            task.cancel()

        self._tasks.clear()

        self._is_running = False

    async def observe(self) -> BotInfo:
        """Observes the world

        Returns:
            The bot's observation of the world.
        """

        if not self._is_running:
            raise RuntimeError(Bot.BOT_NOT_RUNNING_ERROR_MESSAGE)

        response_data = await self._api_client.post("/observe", {})

        jsonschema.validate(
            instance=response_data, schema=BOT_OBSERVE_RESPONSE_DATA_JSON_SCHEMA
        )

        response = BotInfo(response_data["bot"])

        return response

    async def create_action(
        self,
        name: str,
        description: str,
        parameters: List[ActionCreationParameter],
        program: object,
    ):
        """Creates a composite action.

        Args:
            name: The name of the action.
            description: The description of the action.
            parameters: The parameters of the action.
            program: The program of the action.
        """

        if not self._is_running:
            raise RuntimeError(Bot.BOT_NOT_RUNNING_ERROR_MESSAGE)

        # Check duplicate parameter names
        if len({parameter["name"] for parameter in parameters}) != len(parameters):
            raise ValueError("duplicate parameter names")

        response_data = await self._api_client.post(
            "/actions",
            {
                "name": name,
                "description": description,
                "parameters": [
                    {
                        "name": parameter["name"],
                        "description": parameter["description"],
                        "type": parameter["type"],
                        "variable": parameter["variable"],
                    }
                    for parameter in parameters
                ],
                "program": program,
            },
        )

        jsonschema.validate(
            instance=response_data, schema=BOT_ACTIONS_POST_RESPONSE_DATA_JSON_SCHEMA
        )

    async def get_actions(self) -> Dict[str, ActionInfo]:
        """Gets all actions.

        Returns:
            The actions.
        """

        if not self._is_running:
            raise RuntimeError(Bot.BOT_NOT_RUNNING_ERROR_MESSAGE)

        response_data = await self._api_client.get("/actions")

        jsonschema.validate(
            instance=response_data, schema=BOT_ACTIONS_GET_RESPONSE_DATA_JSON_SCHEMA
        )

        # No duplicate names
        assert len({action["name"] for action in response_data["items"]}) == len(
            response_data["items"]
        )

        # No duplicate parameter names of each action
        for action in response_data["items"]:
            assert len(
                {parameter["name"] for parameter in action["parameters"]}
            ) == len(action["parameters"])

        return {
            action["name"]: ActionInfo(
                {
                    "name": action["name"],
                    "description": action["description"],
                    "parameters": {
                        parameter["name"]: {
                            "name": parameter["name"],
                            "description": parameter["description"],
                            "type": parameter["type"],
                        }
                        for parameter in action["parameters"]
                    },
                }
            )
            for action in response_data["items"]
        }

    async def create_job(self, action: str, args: Dict[str, Any]) -> str:
        """Creates a job.

        Args:
            action: The action name of the job.
            args: The arguments of the job.

        Returns:
            The ID of the created job.
        """

        if not self._is_running:
            raise RuntimeError(Bot.BOT_NOT_RUNNING_ERROR_MESSAGE)

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

        if not self._is_running:
            raise RuntimeError(Bot.BOT_NOT_RUNNING_ERROR_MESSAGE)

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

        if not self._is_running:
            raise RuntimeError(Bot.BOT_NOT_RUNNING_ERROR_MESSAGE)

        await self._api_client.post(f"/jobs/{job}/start", {})

    async def pause_job(self, job: str):
        """Pauses a job.

        Args:
            job: The ID of the job to pause.
        """

        if not self._is_running:
            raise RuntimeError(Bot.BOT_NOT_RUNNING_ERROR_MESSAGE)

        await self._api_client.post(f"/jobs/{job}/pause", {})

    async def resume_job(self, job: str):
        """Resumes a job.

        Args:
            job: The ID of the job to resume.
        """

        if not self._is_running:
            raise RuntimeError(Bot.BOT_NOT_RUNNING_ERROR_MESSAGE)

        await self._api_client.post(f"/jobs/{job}/resume", {})

    async def cancel_job(self, job: str):
        """Cancels a job.

        Args:
            job: The ID of the job to cancel.
        """

        if not self._is_running:
            raise RuntimeError(Bot.BOT_NOT_RUNNING_ERROR_MESSAGE)

        await self._api_client.post(f"/jobs/{job}/cancel", {})

    async def _update_events(self):
        # A datetime DateTime of the last update
        last_updated: datetime = datetime.now()

        while True:
            await asyncio.sleep(Bot.UPDAVE_EVENTS_INTERVAL)

            try:
                response_data = await self._api_client.get(
                    "/events",
                    {
                        "since": last_updated.isoformat(),
                    },
                )

            except Exception as e:
                self._logger.error(f"Failed to update events: {e}")
                continue

            try:
                jsonschema.validate(
                    instance=response_data, schema=BOT_EVENTS_RESPONSE_DATA_JSON_SCHEMA
                )

            except jsonschema.ValidationError as e:
                raise jsonschema.ValidationError(f"invalid response from bot API: {e}")

            # Invoke the events.
            for event in response_data["items"]:
                # Allow other tasks to run.
                await asyncio.sleep(0)

                # Update the last updated time if the event is newer.
                updated = datetime.fromisoformat(event["updated"])
                if updated > last_updated:
                    last_updated = updated

                # Invoke the event handler.
                event_handlers = self._event_handlers.get(event["name"], [])
                for event_handler in event_handlers:
                    await event_handler(event)

    async def _update_status(self):
        while True:
            await asyncio.sleep(Bot.UPDATE_STATUS_INTERVAL)

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
