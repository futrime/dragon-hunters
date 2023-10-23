import queue


class TaskTree:
    def __init__(self):
        self.prev_item: str = ""
        self.required_item: dict[str, int] = {}
        self.condition: str = ""
        self.type: str = ""
        self.next_layer: list[list[TaskTree]] = []

    def __str__(self) -> str:
        return f"{self.required_item}, {self.condition}, {self.type}, {self.next_layer}"

    def get_current_action(
        self, kb, current_status: dict, max_num: int = 5
    ) -> list[tuple[str, str]]:
        task_queue = queue.Queue()
        option_queue = queue.Queue()
        task_queue.put(self)
        while not task_queue.empty():
            current_task = task_queue.get()
            index = 0
            flag = False
            if current_task.type == "crafting_table":
                if "crafting_table" not in current_status:
                    this_task, success = kb.get_task_tree({"crafting_table": 1})
                    task_queue.put(this_task)
                    flag = True
                else:
                    for key, value in current_task.required_item.items():
                        if key not in current_status or current_status[key] < value:
                            for new_task in current_task.next_layer[index]:
                                task_queue.put(new_task)
                            flag = True
                        index += 1
                if not flag:
                    option_queue.put(current_task)
            elif current_task.type == "furnace":
                if "furnace" not in current_status:
                    if "furnace" not in current_status:
                        this_task, success = kb.get_task_tree({"furnace": 1})
                        task_queue.put(this_task)
                    flag = True
                else:
                    for key, value in current_task.required_item.items():
                        if key not in current_status or current_status[key] < value:
                            for new_task in current_task.next_layer[index]:
                                task_queue.put(new_task)
                            flag = True
                        index += 1
                if not flag:
                    option_queue.put(current_task)
            elif current_task.type == "player" or current_task.type == "":
                for key, value in current_task.required_item.items():
                    if key not in current_status or current_status[key] < value:
                        for new_task in current_task.next_layer[index]:
                            task_queue.put(new_task)
                        flag = True
                    index += 1
                if not flag:
                    option_queue.put(current_task)
            else:
                if self._fit_condition(current_task.condition, current_status):
                    option_queue.put(current_task)
                else:
                    this_task, success = kb.get_task_tree(
                        {self._get_condition(current_task.condition): 1}
                    )
                    task_queue.put(this_task)
            if len(option_queue.queue) > max_num:
                break
        tips_list = []
        for _ in range(len(option_queue.queue)):
            this_option = option_queue.get()
            if this_option.type == "crafting_table":
                this_tip = f"to craft {this_option.prev_item}, you need: "
                for key, value in this_option.required_item.items():
                    this_tip += f"{key} * {value}, "
                tips_list.append(
                    (f"craft {this_option.prev_item} with crafting table", this_tip)
                )
            elif this_option.type == "furnace":
                this_tip = (
                    f"to smelt {list(this_option.required_item.keys())[0]}, you need: "
                )
                for key, value in this_option.required_item.items():
                    this_tip += f"{key}*{value}, "
                tips_list.append(
                    (
                        f"smelt {list(this_option.required_item.keys())[0]} with furnace",
                        this_tip,
                    )
                )
            elif this_option.type == "player":
                this_tip = f"to craft {this_option.prev_item}, you need: "
                for key, value in this_option.required_item.items():
                    this_tip += f"{key}*{value}, "
                tips_list.append(
                    (f"craft {this_option.prev_item} with player crafting", this_tip)
                )
            elif this_option.type == "mine":
                if "silk_touch" in this_option.condition:
                    continue
                if this_option.condition == "":
                    this_tip = ""
                else:
                    this_tip = f"to mine {list(this_option.required_item.keys())[0]}, you need: {this_option.condition}"
                if this_option.prev_item.endswith(
                    "log"
                ) or this_option.prev_item.endswith("wood"):
                    tips_list.append(
                        (
                            "mine wood or log to get wood or log",
                            "there are oak_log, birch_log, spruce_log, jungle_log, acacia_log, dark_oak_log, mangrove_log and oak_wood, birch_wood, spruce_wood, jungle_wood, acacia_wood, dark_oak_wood, mangrove_wood in Minecraft",
                        )
                    )
                else:
                    tips_list.append(
                        (
                            f"mine {list(this_option.required_item.keys())[0]} to get {this_option.prev_item}",
                            this_tip,
                        )
                    )
            elif this_option.type == "combat":
                this_tip = ""
                tips_list.append(
                    (
                        f"kill {list(this_option.required_item.keys())[0]} to get {this_option.prev_item}",
                        this_tip,
                    )
                )
        return tips_list

    def _fit_condition(self, condition: str, current_status: dict) -> bool:
        if condition == "":
            return True
        else:
            if (
                "wooden_pickaxe" in condition
                and "wooden_pickaxe" not in current_status
                and "stone_pickaxe" not in current_status
                and "iron_pickaxe" not in current_status
                and "diamond_pickaxe" not in current_status
                and "golden_pickaxe" not in current_status
                and "netherite_pickaxe" not in current_status
            ):
                return False
            if (
                "stone_pickaxe" in condition
                and "stone_pickaxe" not in current_status
                and "iron_pickaxe" not in current_status
                and "diamond_pickaxe" not in current_status
                and "netherite_pickaxe" not in current_status
            ):
                return False
            if (
                "iron_pickaxe" in condition
                and "iron_pickaxe" not in current_status
                and "diamond_pickaxe" not in current_status
                and "netherite_pickaxe" not in current_status
            ):
                return False
            if (
                "diamond_pickaxe" in condition
                and "diamond_pickaxe" not in current_status
                and "netherite_pickaxe" not in current_status
            ):
                return False
            if (
                "netherite_pickaxe" in condition
                and "netherite_pickaxe" not in current_status
            ):
                return False

        return True

    def _get_condition(self, condition: str) -> str:
        conds = condition.split(" ")
        for cond in conds:
            if "pickaxe" in cond:
                return cond
