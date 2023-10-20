import os

from langchain.prompts import PromptTemplate

from . import tools


class Prompt:
    def __init__(
        self,
        api_list=None,
        event=None,
        fsm=None,
    ):
        self.FSM = fsm
        if api_list == None:
            api_list = tools.api_list()
        self.api_list = api_list
        self.event = event

    def __call__(self, event):
        return self.generate_prompt(event)

    def generate_prompt(self, event):
        self.event = event
        prompt_template_dir = "prompt_template/main_prompt_template"
        prompt_template_str = tools.file_loader(prompt_template_dir)
        prompt_template = PromptTemplate.from_template(prompt_template_str)
        example = self.example_generator()
        game_info = self.env_generator()
        how_to_code = self.code_format_generator()
        tips = self.tips_loader()
        recommended_action = self.fsm_generator()
        try:
            ans_prompt = prompt_template.format(
                game_info=game_info,
                how_to_code=how_to_code,
                tips=tips,
                example=example,
                recommended_action=recommended_action,
            )
            return ans_prompt
        except Exception:
            raise RuntimeError("Some issues happened while generating the main prompt")

    # warning: should be rewritten if we want to use dynamic knowledge database.
    def tips_loader(self, hand_written=True):
        tips_dir = "prompt_template/tips"
        if hand_written:
            tips = tools.file_loader(tips_dir)
            return tips
        else:
            raise RuntimeError("We do not have the automatic tip module!")

    def code_format_generator(self):
        code_format_str = ""
        for api in self.api_list:
            code_format_str += tools.usage_loader(api)
        return f"<code_format>\n{code_format_str}\n<\\code_format>"

    def fsm_generator(self):
        if self.FSM == None:
            return ""
        else:
            try:
                fsm_message = self.FSM(self.event)
                return fsm_message
            except Exception:
                print("Some issues happened while calling FSM.")
                raise

    def example_generator(self):
        api_dir = "prompt_template/APIs"
        example_prompt = ""
        for index, api in enumerate(self.api_list):
            example = tools.file_loader(os.path.join(api_dir, api, "example"))
            example_prompt += f"<example{index+1}>\n{example}<\\example{index+1}>\n"
        return example_prompt

    def env_generator(self):
        assert isinstance(self.event, dict), "event is not a dictionary"
        event = self.event
        inventory = event["inventory"]
        voxels = event["voxels"]
        entities = event["status"]["entities"]
        health = event["status"]["health"]
        food = event["status"]["food"]
        position = event["status"]["position"]
        equipment = event["status"]["equipment"]
        game_info_template_dir = "prompt_template/game_info_prompt"
        game_info_prompt_str = tools.file_loader(game_info_template_dir)
        game_info_prompt_template = PromptTemplate.from_template(game_info_prompt_str)
        try:
            game_info_prompt = game_info_prompt_template.format(
                inventory=str(inventory),
                voxels=str(voxels),
                entities=str(entities),
                health=str(health),
                food=str(food),
                position=str(position),
                equipment=str(equipment),
            )
            return game_info_prompt
        except Exception:
            print(
                f"""Unable to fill in the prompt.
            Please check the file at: {game_info_template_dir}.
            Make sure it is in the corrected format and corresponding to info that we want."""
            )
            raise
