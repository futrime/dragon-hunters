import asyncio
import copy
import logging
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, List, TypedDict

import jsonschema

from policymaker.bot_apis.get_events_response import GetEventsResponse
from policymaker.bot_apis.get_status_response import GetStatusResponse

from .bot_apis.action_data import ActionData
from .bot_apis.client import Client as BotApiClient
from .bot_apis.event_data import EventData
from .bot_apis.get_actions_response import GetActionsResponse
from .bot_apis.get_jobs_response import GetJobsResponse
from .bot_apis.job_data import JobData
from .bot_apis.observation_data import ObservationData
from .bot_apis.post_actions_response import PostActionsResponse
from .bot_apis.post_jobs_response import PostJobsResponse
from .bot_apis.post_observe_response import PostObserveResponse


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
            str, List[Callable[[EventData], Coroutine[Any, Any, None]]]
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

        PostActionsResponse(response_data)

    async def get_actions(self) -> Dict[str, ActionData]:
        """Gets all actions.

        Returns:
            The actions.
        """

        if not self._is_running:
            raise RuntimeError(Bot.BOT_NOT_RUNNING_ERROR_MESSAGE)

        response_data = await self._api_client.get("/actions")

        return GetActionsResponse(response_data).data()

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

        PostJobsResponse(response_data)

        return response_data["id"]

    async def get_jobs(self) -> Dict[str, JobData]:
        """Gets all jobs.

        Returns:
            The jobs.
        """

        if not self._is_running:
            raise RuntimeError(Bot.BOT_NOT_RUNNING_ERROR_MESSAGE)

        response_data = await self._api_client.get("/jobs")

        return GetJobsResponse(response_data).data()

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

    async def observe(self) -> ObservationData:
        """Observes the world

        Returns:
            The bot's observation of the world.
        """

        if not self._is_running:
            raise RuntimeError(Bot.BOT_NOT_RUNNING_ERROR_MESSAGE)

        response_data = await self._api_client.post("/observe", {})

        return PostObserveResponse(response_data).data()

    def on_event(self, event: str, handler: Callable[[EventData], Coroutine]):
        """Registers an event handler.

        Args:
            event: The name of the event.
            handler: The event handler.
        """

        if event not in self._event_handlers:
            self._event_handlers[event] = []

        self._event_handlers[event].append(handler)

    def off_event(self, event: str, handler: Callable[[EventData], Coroutine]):
        """Unregisters an event handler.

        Args:
            event: The name of the event.
            handler: The event handler.
        """

        if event not in self._event_handlers:
            return

        self._event_handlers[event].remove(handler)

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

                response = GetEventsResponse(response_data)

                # Invoke the events.
                for event in response.data().values():
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

            except Exception as e:
                self._logger.error(f"Failed to update events: {e}")
                continue

    async def _update_status(self):
        while True:
            await asyncio.sleep(Bot.UPDATE_STATUS_INTERVAL)

            try:
                response_data = await self._api_client.get("/status")

                GetStatusResponse(response_data)

                # Nothing to do currently.

            except Exception as e:
                self._logger.error(f"Failed to update status: {e}")
                continue
