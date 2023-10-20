from abc import ABC, abstractmethod

from . import tools


class Connection(ABC):
    def __init__(self, name="bot", api_list=None, start_max_trying=1):
        self.name = name
        if api_list is not None:
            self.api_list = api_list
        else:
            self.api_list = tools.api_list()
        self.starting = False
        self.start_max_trying = start_max_trying

    @abstractmethod
    def start_env(self):
        """
        What we pass to the interface method:
            name of our bot.
        What we get from the return value:
            if started successfully->return True.
            else -> return false.
        """
        pass

    @abstractmethod
    def step_env(self, command):
        """
        What we pass to the interface method:
            our command.
        It shouldn't return anything.
        Attention! It should be a sync method.
        """
        pass

    @abstractmethod
    def observe_env(self):
        """
        It should return an event dictionary.
        like this:
        ```
        assert isinstance(event, dict) "event should be a dictionary"
        return event
        ```

        format:
        ```
        event = {
            "inventory":{"dirt":10},
            "voxels":["dirt", "oak_log"],
            "status":{
                "entities":[],
                "food":20,
                "position":[0.0,64.0,0.0],
                "equipment":[],
                "health":20}
            }
        ```
        """
        pass

    def step(self, prompt):
        if self.starting:
            command_list = self.parse(prompt)
            for command in command_list:
                try:
                    self.step_env(command)
                except Exception:
                    # should be modified so program can continue to run even if error happended.
                    raise RuntimeError(f"Failed while run command:{command}.")
            return self.observe_env()
        else:
            raise RuntimeError("You should start the connection before call step!")

    def start(self):
        success = False
        self.starting = False
        for _ in range(self.start_max_trying):
            if self.start_env():
                success = True
                break
        if success:
            self.starting = True
            return self.observe_env()
        else:
            raise RuntimeError("Unable to start connection")

    def parse(self, prompt):
        lines = prompt.splitlines()
        command_list = []
        for line in lines:
            line = line.replace(" ", "")
            for api in self.api_list:
                command = tools.translate(line, api)
                if command is not None:
                    command_list.append(command)
        if command_list:
            return command_list
        else:
            raise RuntimeError("Awful prompt! Unable to fetch command.")

    def get_API_list(self):
        return self.api_list
