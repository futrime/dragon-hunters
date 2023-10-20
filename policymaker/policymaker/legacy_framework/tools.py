import json
import os
import re

from langchain.prompts import PromptTemplate


def file_loader(dir):
    try:
        with open(dir, "r") as file:
            string = file.read()
            return string
    except Exception:
        print(
            f"""Unable to load prompt_template.
                Your template dir:{dir}"""
        )
        raise


def api_list():
    DIR = "prompt_template/APIs"
    try:
        api_list = [d for d in os.listdir(DIR) if os.path.isdir(os.path.join(DIR, d))]
        return api_list
    except Exception:
        print(
            f"""Unable to list APIs.
                Your APIs dir:{DIR}"""
        )
        raise


def usage_loader(name):
    DIR = f"prompt_template/APIs/{name}"
    usage_dir = os.path.join(DIR, "usage")
    attention_dir = os.path.join(DIR, "attention")
    usage = file_loader(usage_dir)
    attention = file_loader(attention_dir)
    return f"<{name}>\n{usage}attention:{attention}<\\{name}>\n"


def config_loader(api):
    DIR = "prompt_template/APIs"
    try:
        with open(os.path.join(DIR, api, "config.json"), "r") as f:
            config = json.load(f)
            return config
    except Exception:
        print(f'Unable to load{os.path.join(DIR,api,"config.json")}')
        raise


def translate(text, api):
    config = config_loader(api)
    valid_regex = config["valid_regex"]
    arg_num = config["arg_num"]
    template_str = config["template"]
    valid_pattern = re.compile(valid_regex)
    match = valid_pattern.match(text)
    assert isinstance(arg_num, int), "Variable arg_num is not an int!"
    assert arg_num >= 0, "Variable arg_num should be larger than zero!"
    if match:
        arg_list = {}
        for index in range(arg_num):
            arg_pattern = re.compile(config[f"arg{index+1}_regex"])
            arg_search = arg_pattern.search(text)
            assert arg_search, f"Unable to extract arg{index+1}!"
            arg_list[f"arg{index+1}"] = arg_search.group(0)
        template = PromptTemplate.from_template(template_str)
        try:
            command = template.format(**arg_list)
            return command
        except Exception:
            raise RuntimeError(f"template of API:{api} failed to fill up!")
    else:
        return None


def openai_api_key_loader(openai_key=None):
    if openai_key is None:
        try:
            key = file_loader(".openai_api")
            key = re.sub(r"\s", "", key)
        except Exception:
            raise RuntimeError('Please set "your_openai_API_key!')
    else:
        key = openai_key
    return key
