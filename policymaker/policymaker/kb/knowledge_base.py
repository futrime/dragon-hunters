import copy
import json
import os
import pathlib


class KnowledgeBase:
    def __init__(
        self,
        base_path: str = os.path.join(os.getcwd(), "data"),
        recipe: bool = True,
        loot: bool = True,
        drop: bool = True,
        resume: bool = False,
    ):
        """
        :param base_path: str, path to the knowledge base
        :param recipe: load recipe or not
        :param loot: load loot or not
        """
        self.__base_path = base_path
        self.load(recipe, loot, drop, resume)

    def load(self, recipe, loot, drop, resume):
        """
        :param recipe: load recipe or not
        :param loot: load loot or not
        """
        self.__recipe = recipe
        self.__loot = loot
        self.__drop = drop
        self.__resume = resume
        self.__material_to_crafted = {}
        self.__crafted_to_material = {}
        self.__qa = {}
        if self.__recipe:
            self._load_recipe()
        if self.__loot:
            self._load_loot()
        if self.__drop:
            self._load_drop()
        if self.__resume:
            with open(f"{self.__base_path}/qa.json", "r") as f:
                self.__qa = json.load(f)

    def _load_recipe_shapeless(self, recipe):
        """
        :param recipe: dict, a shapeless recipe
        Load a shapeless recipe
        """
        craft_num = len(recipe["ingredients"])
        if craft_num > 4:
            recipe_type = "crafting_table"
        else:
            recipe_type = "player"

        crafted = recipe["result"]["item"].split(":")[1]
        if crafted not in self.__crafted_to_material:
            self.__crafted_to_material[crafted] = []

        this_recipe = [{"recipe": {}, "type": recipe_type}]

        for ingredient in recipe["ingredients"]:
            if "item" in ingredient:
                if ingredient["item"].split(":")[1] not in self.__material_to_crafted:
                    self.__material_to_crafted[ingredient["item"].split(":")[1]] = [
                        {"item": crafted, "type": recipe_type}
                    ]
                else:
                    for item in self.__material_to_crafted[
                        ingredient["item"].split(":")[1]
                    ]:
                        if item["item"] == crafted:
                            break
                    else:
                        self.__material_to_crafted[
                            ingredient["item"].split(":")[1]
                        ].append({"item": crafted, "type": recipe_type})
                if ingredient["item"].split(":")[1] not in this_recipe[0]["recipe"]:
                    this_recipe[0]["recipe"][ingredient["item"].split(":")[1]] = 1
                else:
                    this_recipe[0]["recipe"][ingredient["item"].split(":")[1]] += 1

        for ingredient in recipe["ingredients"]:
            if isinstance(ingredient, list):
                if len(this_recipe) == 1:
                    for _ in range(len(ingredient) - 1):
                        this_recipe.append(copy.deepcopy(this_recipe[0]))
                for ind, item_ in enumerate(ingredient):
                    if item_["item"].split(":")[1] not in self.__material_to_crafted:
                        self.__material_to_crafted[item_["item"].split(":")[1]] = [
                            {"item": crafted, "type": recipe_type}
                        ]
                    else:
                        for item in self.__material_to_crafted[
                            item_["item"].split(":")[1]
                        ]:
                            if item["item"] == crafted:
                                break
                        else:
                            self.__material_to_crafted[
                                item_["item"].split(":")[1]
                            ].append({"item": crafted, "type": recipe_type})
                    if item_["item"].split(":")[1] not in this_recipe[ind]["recipe"]:
                        this_recipe[ind]["recipe"][item_["item"].split(":")[1]] = 1
                    else:
                        this_recipe[ind]["recipe"][item_["item"].split(":")[1]] += 1
        for ingredient in recipe["ingredients"]:
            if "tag" in ingredient:
                tag = ingredient["tag"].split(":")[1]
                with open(f"{self.__base_path}/tags/items/{tag}.json", "r") as f:
                    tag = json.load(f)
                    recipe_list = tag["values"]
                    for item in recipe_list:
                        if item.startswith("#minecraft:"):
                            recipe_list.remove(item)
                            with open(
                                f"{self.__base_path}/tags/items/{item.split(':')[1]}.json",
                                "r",
                            ) as f:
                                tag = json.load(f)
                                recipe_list.extend(tag["values"])
                    if len(this_recipe) == 1:
                        for _ in range(len(recipe_list) - 1):
                            this_recipe.append(copy.deepcopy(this_recipe[0]))
                    for ind, item_ in enumerate(recipe_list):
                        if item_.split(":")[1] not in self.__material_to_crafted:
                            self.__material_to_crafted[item_.split(":")[1]] = [
                                {"item": crafted, "type": recipe_type}
                            ]
                        else:
                            for item in self.__material_to_crafted[item_.split(":")[1]]:
                                if item["item"] == crafted:
                                    break
                            else:
                                self.__material_to_crafted[item_.split(":")[1]].append(
                                    {"item": crafted, "type": recipe_type}
                                )
                        if item_.split(":")[1] not in this_recipe[ind]["recipe"]:
                            this_recipe[ind]["recipe"][item_.split(":")[1]] = 1
                        else:
                            this_recipe[ind]["recipe"][item_.split(":")[1]] += 1
        self.__crafted_to_material[crafted].extend(this_recipe)

    def _load_recipe_shaped(self, recipe):
        """
        :param recipe: dict, a shaped recipe
        Load a shaped recipe
        """
        for line in recipe["pattern"]:
            if len(line) >= 3:
                recipe_type = "crafting_table"
                break
        else:
            if len(recipe["pattern"]) >= 3:
                recipe_type = "crafting_table"
            else:
                recipe_type = "player"

        crafted = recipe["result"]["item"].split(":")[1]
        if crafted in ["barrel", "campfire", "soul_campfire"]:
            return
        if crafted not in self.__crafted_to_material:
            self.__crafted_to_material[crafted] = []

        this_recipe = [{"recipe": {}, "type": recipe_type}]

        keyToNum = {}
        for line in recipe["pattern"]:
            for char in line:
                if char == " ":
                    continue
                if char not in keyToNum:
                    keyToNum[char] = 1
                else:
                    keyToNum[char] += 1

        for key in recipe["key"]:
            if "item" in recipe["key"][key]:
                if (
                    recipe["key"][key]["item"].split(":")[1]
                    not in self.__material_to_crafted
                ):
                    self.__material_to_crafted[
                        recipe["key"][key]["item"].split(":")[1]
                    ] = [{"item": crafted, "type": recipe_type}]
                else:
                    for item in self.__material_to_crafted[
                        recipe["key"][key]["item"].split(":")[1]
                    ]:
                        if item["item"] == crafted:
                            break
                    else:
                        self.__material_to_crafted[
                            recipe["key"][key]["item"].split(":")[1]
                        ].append({"item": crafted, "type": recipe_type})
                this_recipe[0]["recipe"][
                    recipe["key"][key]["item"].split(":")[1]
                ] = keyToNum[key]

        reqNum = 1
        for key in recipe["key"]:
            if "tag" in recipe["key"][key]:
                tag = recipe["key"][key]["tag"].split(":")[1]
                with open(f"{self.__base_path}/tags/items/{tag}.json", "r") as f:
                    tag = json.load(f)
                    recipe_list = tag["values"]
                    for item in recipe_list:
                        if item.startswith("#minecraft:"):
                            recipe_list.remove(item)
                            with open(
                                f"{self.__base_path}/tags/items/{item.split(':')[1]}.json",
                                "r",
                            ) as f:
                                tag = json.load(f)
                                recipe_list.extend(tag["values"])
                    reqNum = len(recipe_list) * reqNum
            if isinstance(recipe["key"][key], list):
                reqNum = len(recipe["key"][key]) * reqNum

        if reqNum > 1:
            for _ in range(reqNum - 1):
                this_recipe.append(copy.deepcopy(this_recipe[0]))
            flag = False
            for key in recipe["key"]:
                if isinstance(recipe["key"][key], list):
                    flag = True
                    stride = reqNum // len(recipe["key"][key])
                    for ind, item_ in enumerate(recipe["key"][key]):
                        if (
                            item_["item"].split(":")[1]
                            not in self.__material_to_crafted
                        ):
                            self.__material_to_crafted[item_["item"].split(":")[1]] = [
                                {"item": crafted, "type": recipe_type}
                            ]
                        else:
                            for item in self.__material_to_crafted[
                                item_["item"].split(":")[1]
                            ]:
                                if item["item"] == crafted:
                                    break
                            else:
                                self.__material_to_crafted[
                                    item_["item"].split(":")[1]
                                ].append({"item": crafted, "type": recipe_type})
                        for i in range(ind * stride, (ind + 1) * stride):
                            this_recipe[i]["recipe"][
                                item_["item"].split(":")[1]
                            ] = keyToNum[key]

            for key in recipe["key"]:
                if "tag" in recipe["key"][key]:
                    tag = recipe["key"][key]["tag"].split(":")[1]
                    with open(f"{self.__base_path}/tags/items/{tag}.json", "r") as f:
                        tag = json.load(f)
                        recipe_list = tag["values"]
                        for item in recipe_list:
                            if item.startswith("#minecraft:"):
                                recipe_list.remove(item)
                                with open(
                                    f"{self.__base_path}/tags/items/{item.split(':')[1]}.json",
                                    "r",
                                ) as f:
                                    tag = json.load(f)
                                    recipe_list.extend(tag["values"])
                        stride = reqNum // len(recipe_list)
                        for ind, item_ in enumerate(recipe_list):
                            if item_.split(":")[1] not in self.__material_to_crafted:
                                self.__material_to_crafted[item_.split(":")[1]] = [
                                    {"item": crafted, "type": recipe_type}
                                ]
                            else:
                                for item in self.__material_to_crafted[
                                    item_.split(":")[1]
                                ]:
                                    if item["item"] == crafted:
                                        break
                                else:
                                    self.__material_to_crafted[
                                        item_.split(":")[1]
                                    ].append({"item": crafted, "type": recipe_type})
                            if not flag:
                                for i in range(ind * stride, (ind + 1) * stride):
                                    this_recipe[i]["recipe"][
                                        item_.split(":")[1]
                                    ] = keyToNum[key]
                            else:
                                for i in range(ind, reqNum, stride):
                                    this_recipe[i]["recipe"][
                                        item_.split(":")[1]
                                    ] = keyToNum[key]

        self.__crafted_to_material[crafted].extend(this_recipe)

    def _load_recipe_furnace(self, recipe):
        """
        :param recipe: dict, a furnace recipe
        Load a furnace recipe
        """
        crafted = recipe["result"].split(":")[1]

        recipe_type = "furnace"

        if crafted not in self.__crafted_to_material:
            self.__crafted_to_material[crafted] = []

        this_recipe = [{"recipe": {}, "type": recipe_type}]

        if "item" in recipe["ingredient"]:
            if (
                recipe["ingredient"]["item"].split(":")[1]
                not in self.__material_to_crafted
            ):
                self.__material_to_crafted[
                    recipe["ingredient"]["item"].split(":")[1]
                ] = [{"item": crafted, "type": recipe_type}]
            else:
                for item in self.__material_to_crafted[
                    recipe["ingredient"]["item"].split(":")[1]
                ]:
                    if item["item"] == crafted:
                        break
                else:
                    self.__material_to_crafted[
                        recipe["ingredient"]["item"].split(":")[1]
                    ].append({"item": crafted, "type": recipe_type})
            this_recipe[0]["recipe"][recipe["ingredient"]["item"].split(":")[1]] = 1

        if isinstance(recipe["ingredient"], list):
            for _ in range(len(recipe["ingredient"]) - 1):
                this_recipe.append(copy.deepcopy(this_recipe[0]))
            for ind, item in enumerate(recipe["ingredient"]):
                if item["item"].split(":")[1] not in self.__material_to_crafted:
                    self.__material_to_crafted[item["item"].split(":")[1]] = [
                        {"item": crafted, "type": recipe_type}
                    ]
                else:
                    for item in self.__material_to_crafted[item["item"].split(":")[1]]:
                        if item["item"] == crafted:
                            break
                    else:
                        self.__material_to_crafted[item["item"].split(":")[1]].append(
                            {"item": crafted, "type": recipe_type}
                        )
                this_recipe[ind]["recipe"][item["item"].split(":")[1]] = 1

        if "tag" in recipe["ingredient"]:
            tag = recipe["ingredient"]["tag"].split(":")[1]
            with open(f"{self.__base_path}/tags/items/{tag}.json", "r") as f:
                tag = json.load(f)
                recipe_list = tag["values"]
                for item in recipe_list:
                    if item.startswith("#minecraft:"):
                        recipe_list.remove(item)
                        with open(
                            f"{self.__base_path}/tags/items/{item.split(':')[1]}.json",
                            "r",
                        ) as f:
                            tag = json.load(f)
                            recipe_list.extend(tag["values"])
                for _ in range(len(recipe_list) - 1):
                    this_recipe.append(copy.deepcopy(this_recipe[0]))
                for ind, item_ in enumerate(recipe_list):
                    if item_.split(":")[1] not in self.__material_to_crafted:
                        self.__material_to_crafted[item_.split(":")[1]] = [
                            {"item": crafted, "type": recipe_type}
                        ]
                    else:
                        for item in self.__material_to_crafted[item_.split(":")[1]]:
                            if item["item"] == crafted:
                                break
                        else:
                            self.__material_to_crafted[item_.split(":")[1]].append(
                                {"item": crafted, "type": recipe_type}
                            )
                    this_recipe[ind]["recipe"][item_.split(":")[1]] = 1
        self.__crafted_to_material[crafted].extend(this_recipe)

    def _load_recipe(self):
        """
        Load recipe from knowledge base
        """
        recipe_path = f"{self.__base_path}/recipes"

        for recipe_file in os.listdir(recipe_path):
            with open(f"{recipe_path}/{recipe_file}", "r") as f:
                recipe = json.load(f)
                craft_type = recipe["type"]

                if craft_type == "minecraft:crafting_shapeless":
                    self._load_recipe_shapeless(recipe)
                elif craft_type == "minecraft:crafting_shaped":
                    self._load_recipe_shaped(recipe)
                elif craft_type == "minecraft:smelting":
                    self._load_recipe_furnace(recipe)

    def _load_loot_table(self, loot, name):
        """
        :param loot: dict, a loot table
        :param name: str, name of the loot table
        Load a loot table
        """
        if "pools" not in loot:
            return

        recipe_type = "combat"

        for pool in loot["pools"]:
            for item in pool["entries"]:
                if "name" not in item:
                    continue
                item_name = item["name"].split(":")[1]
                if item_name not in self.__crafted_to_material:
                    self.__crafted_to_material[item_name] = [
                        {"recipe": {name: 1}, "type": recipe_type}
                    ]
                else:
                    for item_ in self.__crafted_to_material[item_name]:
                        if item_ == {"recipe": {name: 1}, "type": recipe_type}:
                            break
                    else:
                        self.__crafted_to_material[item_name].append(
                            {"recipe": {name: 1}, "type": recipe_type}
                        )
                if name not in self.__material_to_crafted:
                    self.__material_to_crafted[name] = [
                        {"item": item_name, "type": recipe_type}
                    ]
                else:
                    for item_ in self.__material_to_crafted[name]:
                        if item_ == {"item": item_name, "type": recipe_type}:
                            break
                    else:
                        self.__material_to_crafted[name].append(
                            {"item": item_name, "type": recipe_type}
                        )

    def _load_loot(self):
        """
        Load loot from knowledge base
        """

        loot_path = f"{self.__base_path}/loot_tables/entities"
        for loot_file in os.listdir(loot_path):
            if loot_file.endswith(".json"):
                with open(f"{loot_path}/{loot_file}", "r") as f:
                    loot = json.load(f)
                    self._load_loot_table(loot, loot_file.split(".")[0])

    def _load_drop_table(self, drop, name):
        """
        :param drop: dict, a drop table
        :param name: str, name of the drop table
        Load a drop table
        """
        if "pools" not in drop:
            return

        recipe_type = "mine"

        for pool in drop["pools"]:
            for item in pool["entries"]:
                if "children" in item:
                    for child in item["children"]:
                        if "name" not in child:
                            continue
                        item_name = child["name"].split(":")[1]
                        if item_name not in self.__crafted_to_material:
                            self.__crafted_to_material[item_name] = [
                                {"recipe": {name: 1}, "type": recipe_type}
                            ]
                        else:
                            for item_ in self.__crafted_to_material[item_name]:
                                if item_ == {"recipe": {name: 1}, "type": recipe_type}:
                                    break
                            else:
                                self.__crafted_to_material[item_name].append(
                                    {"recipe": {name: 1}, "type": recipe_type}
                                )
                        if name not in self.__material_to_crafted:
                            self.__material_to_crafted[name] = [
                                {"item": item_name, "type": recipe_type}
                            ]
                        else:
                            for item_ in self.__material_to_crafted[name]:
                                if item_ == {"item": item_name, "type": recipe_type}:
                                    break
                            else:
                                self.__material_to_crafted[name].append(
                                    {"item": item_name, "type": recipe_type}
                                )
                if "name" not in item:
                    continue
                item_name = item["name"].split(":")[1]
                if item_name not in self.__crafted_to_material:
                    self.__crafted_to_material[item_name] = [
                        {"recipe": {name: 1}, "type": recipe_type}
                    ]
                else:
                    for item_ in self.__crafted_to_material[item_name]:
                        if item_ == {"recipe": {name: 1}, "type": recipe_type}:
                            break
                    else:
                        self.__crafted_to_material[item_name].append(
                            {"recipe": {name: 1}, "type": recipe_type}
                        )
                if name not in self.__material_to_crafted:
                    self.__material_to_crafted[name] = [
                        {"item": item_name, "type": recipe_type}
                    ]
                else:
                    for item_ in self.__material_to_crafted[name]:
                        if item_ == {"item": item_name, "type": recipe_type}:
                            break
                    else:
                        self.__material_to_crafted[name].append(
                            {"item": item_name, "type": recipe_type}
                        )

    def _add_condition(self, drop, name):
        if "pools" not in drop:
            return

        for pool in drop["pools"]:
            if "conditions" in pool:
                for condition in pool["conditions"]:
                    condition_str = self._get_condition(condition)
                    if condition_str == "":
                        continue
                    for item in pool["entries"]:
                        if "children" in item:
                            for child in item["children"]:
                                if "name" not in child:
                                    continue
                                item_name = child["name"].split(":")[1]
                                for item_ in self.__crafted_to_material[item_name]:
                                    if (
                                        item_["recipe"] == {name: 1}
                                        and item_["type"] == "mine"
                                    ):
                                        if "condition" not in item_:
                                            item_["condition"] = condition_str
                                        else:
                                            item_["condition"] += (
                                                " and " + condition_str
                                            )
                                        break
                                for item_ in self.__material_to_crafted[name]:
                                    if (
                                        item_["item"] == item_name
                                        and item_["type"] == "mine"
                                    ):
                                        if "condition" not in item_:
                                            item_["condition"] = condition_str
                                        else:
                                            item_["condition"] += (
                                                " and " + condition_str
                                            )
                                        break

                        if "name" not in item:
                            continue
                        item_name = item["name"].split(":")[1]
                        for item_ in self.__crafted_to_material[item_name]:
                            if item_["recipe"] == {name: 1} and item_["type"] == "mine":
                                if "condition" not in item_:
                                    item_["condition"] = condition_str
                                else:
                                    item_["condition"] += " and " + condition_str
                                break
                        for item_ in self.__material_to_crafted[name]:
                            if item_["item"] == item_name and item_["type"] == "mine":
                                if "condition" not in item_:
                                    item_["condition"] = condition_str
                                else:
                                    item_["condition"] += " and " + condition_str
                                break
            for item in pool["entries"]:
                if "children" in item:
                    for child in item["children"]:
                        if "name" not in child:
                            continue
                        if "conditions" not in child:
                            continue
                        item_name = child["name"].split(":")[1]
                        for condition in child["conditions"]:
                            condition_str = self._get_condition(condition)
                            if condition_str == "":
                                continue
                            for item_ in self.__crafted_to_material[item_name]:
                                if (
                                    item_["recipe"] == {name: 1}
                                    and item_["type"] == "mine"
                                ):
                                    if "condition" not in item_:
                                        item_["condition"] = condition_str
                                    else:
                                        item_["condition"] += " and " + condition_str
                                    break
                            for item_ in self.__material_to_crafted[name]:
                                if (
                                    item_["item"] == item_name
                                    and item_["type"] == "mine"
                                ):
                                    if "condition" not in item_:
                                        item_["condition"] = condition_str
                                    else:
                                        item_["condition"] += " and " + condition_str
                                    break

                if "name" not in item:
                    continue
                item_name = item["name"].split(":")[1]
                if "conditions" not in item:
                    continue
                for condition in item["conditions"]:
                    condition_str = self._get_condition(condition)
                    if condition_str == "":
                        continue
                    for item_ in self.__crafted_to_material[item_name]:
                        if item_["recipe"] == {name: 1} and item_["type"] == "mine":
                            if "condition" not in item_:
                                item_["condition"] = condition_str
                            else:
                                item_["condition"] += " and " + condition_str
                            break
                    for item_ in self.__material_to_crafted[name]:
                        if item_["item"] == item_name and item_["type"] == "mine":
                            if "condition" not in item_:
                                item_["condition"] = condition_str
                            else:
                                item_["condition"] += " and " + condition_str
                            break

    def _get_condition(self, condition):
        """
        :param condition: dict, a condition dict
        :return: str, the condition
        """
        if condition["condition"] == "minecraft:match_tool":
            if "items" in condition["predicate"]:
                condition_str = "tool: "
                for item in condition["predicate"]["items"]:
                    condition_str += item.split(":")[1] + ","
                return condition_str[:-1]
            elif "enchantments" in condition["predicate"]:
                condition_str = "enchant:"
                for enchant in condition["predicate"]["enchantments"]:
                    condition_str += enchant["enchantment"].split(":")[1] + ","
                return condition_str[:-1]
        elif condition["condition"] == "minecraft:table_bonus":
            return "table_bonus"
        elif condition["condition"] == "minecraft:alternative":
            condition_str = ""
            for condition_ in condition["terms"]:
                condition_str += self._get_condition(condition_) + " or "
            return condition_str[:-4]
        elif condition["condition"] == "minecraft:inverted":
            condition_str = "not "
            condition_str += self._get_condition(condition["term"])
            return condition_str
        else:
            return ""

    def _add_mine_condition(self):
        with open(f"{self.__base_path}/blocks.json") as f:
            blocks = json.load(f)
            for block in blocks:
                if block["material"] == "mineable/pickaxe":
                    if "harvestTools" not in block:
                        continue
                    condition_str = "tool: "
                    if "737" in block["harvestTools"]:
                        condition_str += "any pickaxe"
                    elif "742" in block["harvestTools"]:
                        condition_str += "pickaxe better than stone"
                    elif "752" in block["harvestTools"]:
                        condition_str += "pickaxe better than iron"
                    elif "757" in block["harvestTools"]:
                        condition_str += "pickaxe better than diamond"
                    elif "762" in block["harvestTools"]:
                        condition_str += "netherite pickaxe"
                    else:
                        continue
                    if block["name"] in self.__material_to_crafted:
                        for item in self.__material_to_crafted[block["name"]]:
                            if item["type"] == "mine":
                                if "condition" not in item:
                                    item["condition"] = condition_str
                                else:
                                    item["condition"] += " and " + condition_str
                                for item_ in self.__crafted_to_material[item["item"]]:
                                    if (
                                        item_["recipe"] == {block["name"]: 1}
                                        and item_["type"] == "mine"
                                    ):
                                        if "condition" not in item_:
                                            item_["condition"] = condition_str
                                        else:
                                            item_["condition"] += (
                                                " and " + condition_str
                                            )
                                        break

    def _load_drop(self):
        """
        Load drop from knowledge base
        """
        drop_path = f"{self.__base_path}/loot_tables/blocks"
        for drop_file in os.listdir(drop_path):
            if drop_file.endswith(".json"):
                with open(f"{drop_path}/{drop_file}", "r") as f:
                    drop = json.load(f)
                    self._load_drop_table(drop, drop_file.split(".")[0])

        for drop_file in os.listdir(drop_path):
            if drop_file.endswith(".json"):
                with open(f"{drop_path}/{drop_file}", "r") as f:
                    drop = json.load(f)
                    self._add_condition(drop, drop_file.split(".")[0])

        self._add_mine_condition()

    def add_qa(self, question: str = "", answer: str = ""):
        """
        :param question: str, question
        :param answer: str, answer
        Add a question-answer pair to the knowledge base
        """
        self.__qa[question] = answer
        if question == "":
            question = input("Question: ")
        if answer == "":
            answer = input("Answer: ")
        with open(f"{self.__base_path}/qa.json", "w") as f:
            qa = json.dumps(self.__qa, indent=4)
            f.write(qa)

    def get_qa(self, key_word: str) -> dict[str, str]:
        """
        :param question: str, question
        :return: str, answer
        Get the answer of a question
        """
        qa_dict = {}
        for question in self.__qa:
            if key_word in question:
                qa_dict[question] = self.__qa[question]
        return qa_dict

    @property
    def material_to_crafted(self):
        return self.__material_to_crafted

    @property
    def crafted_to_material(self):
        return self.__crafted_to_material
