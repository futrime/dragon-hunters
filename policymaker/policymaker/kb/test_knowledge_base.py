import unittest
from .knowledge_base import KnowledgeBase


class KnowledgeBaseTest(unittest.TestCase):
    def test_load_nothing(self):
        kb: KnowledgeBase = KnowledgeBase()

        kb.load(recipe=False, loot=False, drop=False, resume=False)

        del kb

    def test_load_recipe_only(self):
        kb: KnowledgeBase = KnowledgeBase()

        kb.load(recipe=True, loot=False, drop=False, resume=False)

        del kb

    def test_task_loading(self):
        kb = KnowledgeBase()

        goal = {"diamond_pickaxe": 1}

        test = kb.get_task_tree(goal)

        current_status = {
            "crafting_table": 1,
            "oak_planks": 1,
            "wooden_pickaxe": 1,
            "furnace": 1,
            "stone_pickaxe": 1,
            "iron_ingot": 2,
            "iron_pickaxe": 1,
            "diamond_pickaxe": 1,
        }

        with open("test.txt", "a") as f:
            f.write(f"current_status: {current_status}\n")
            f.write("task&tips:\n")
            print(f"final goal: {goal}")
            print()
            print(f"current_status: {current_status}")
            print()
            print("task&tips:")

            tip_list = test[0].get_current_action(
                kb=kb,
                current_status=current_status,
                max_num=10,
            )
            tip_list = list({}.fromkeys(tip_list).keys())
            for item in tip_list:
                print(item)
                f.write(f"{item}\n")

            f.write("\n")
            print()
