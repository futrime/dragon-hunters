from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from . import fsm, prompt, tools


class Agent:
    def __init__(
        self,
        connection,
        openai_api_key=None,
        fsm=fsm.fsm_diamond_pickaxe,
        gpt4=False,
        restart_limit=10,
    ):
        self.key = tools.openai_api_key_loader(openai_key=openai_api_key)
        self.connection = connection
        self.prompt = prompt.Prompt(api_list=connection.get_API_list(), fsm=fsm)
        if gpt4:
            model_name = "GPT-4"
        else:
            model_name = "gpt-3.5-turbo"
        self.chat_model = ChatOpenAI(model=model_name, openai_api_key=self.key)
        self.restart_limit = restart_limit

    def __call__(self):
        for _ in range(self.restart_limit):
            try:
                self.run()
            except Exception as e:
                print(f"Restart due to error: {e}")

    def run(self):
        event = self.connection.start()
        while True:
            ##
            print(f"event:{event}")
            ##

            prompt_str = self.prompt(event)

            ##
            print(f"prompt:{prompt_str}")
            ##

            ans = self.chat_model.predict(prompt_str)

            ##
            print(f"ans:{ans}")
            ##

            event = self.connection.step(ans)
