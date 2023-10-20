"""
Attention! The file is silly because I don't want to take the ridiculous logic serious.
(but actually it works well) 
"""


import random

# It is a silly way to accomplish it and should be improved.


def diamond(num):
    if num > 2:
        return "collect diamond now! just call mineBlock to mine diamond_ore. num can be bigger like 6."
    else:
        return "explore now. try direction like (1,0,0) (-1,0,0) (0,0,1), (0,0,-1),(0,-1,0)"


def fsm_diamond_pickaxe(events):
    rand = random.randint(1, 10)
    inventory = events["inventory"]
    position = events["status"]["position"]
    if "wooden_pickaxe" in inventory:
        if "cobblestone" not in inventory:
            return "think how to collect some stone and collect stone first!"
        if "stone_pickaxe" not in inventory:
            return "create a  stone_pickaxe now!"
        if "coal" not in inventory:
            return "collect some coal now. your y position should be bigger than 0"
        if "iron_pickaxe" not in inventory:
            if "raw_iron" not in inventory and "iron_ingot" not in inventory:
                return (
                    "collect some iron_ore now. your y position should be bigger than 0"
                )
            else:
                if "raw_iron" in inventory:
                    return "smelt raw_iron now. make sure you have a furnace in your inventory"
                else:
                    return "create a iron_pickaxe"
        else:
            if position["y"] <= 0:
                return "go up, try dirction (0,1,0),distance:5"
            if "diamond" not in inventory:
                return diamond(rand)
            else:
                if "diamond_pickaxe" not in inventory:
                    if inventory["diamond"] < 3:
                        return diamond(rand)
                    return "create diamond_pickaxe now!"
                else:
                    raise RuntimeError("diamond_pickaxe finished!")
    else:
        if "crafting_table" in inventory:
            if "oak_log" in inventory:
                return "use all your oak_log to create oak_planks now"
            if "stick" in inventory and inventory["stick"] >= 2:
                return "create wooden_pickaxe now"
            else:
                if "oak_planks" in inventory and inventory["oak_planks"] >= 21:
                    return "create 9 times stick now"
                else:
                    return "collect 10 oak_log"
        else:
            if "oak_log" in inventory:
                return "create oak_planks now"
            else:
                if "oak_planks" in inventory and inventory["oak_planks"] >= 4:
                    return "craft crafting_table now"
                return "collect 10 oak_log"


# normal main world
def fsm_main(events):
    rand = random.randint(1, 10)
    inventory = events["inventory"]
    position = events["status"]["position"]
    if "wooden_pickaxe" in inventory:
        if "cobblestone" not in inventory:
            return "think how to collect some stone and collect stone first!"
        if "stone_pickaxe" not in inventory:
            return "create a  stone_pickaxe now!"
        if "coal" not in inventory:
            return "collect some coal now. your y position should be bigger than 0"
        if "iron_pickaxe" not in inventory:
            if "raw_iron" not in inventory and "iron_ingot" not in inventory:
                return "collect some iron_ore now(more than 7). your y position should be bigger than 0"
            else:
                if "raw_iron" in inventory:
                    return "smelt raw_iron now. make sure you have a furnace in your inventory"
                else:
                    if "bucket" not in inventory:
                        return "create a bucket"
                    return "create a iron_pickaxe"
        else:
            if "bucket" not in inventory and "water_bucket" not in inventory:
                return "craft a bucket now"
            if position["y"] <= -5:
                return "go up, try dirction (0,1,0),distance:5"
            if "diamond" not in inventory:
                if position["y"] >= 15:
                    return "please dig down.direction (0,-1,0)"
                return diamond(rand)
            else:
                if "diamond_pickaxe" not in inventory:
                    if inventory["diamond"] < 3:
                        if position["y"] >= 15:
                            return "please dig down. direction(0,-1,0)"
                        return diamond(rand)
                    return "create diamond_pickaxe now!"
                else:
                    if "flint_and_steel" not in inventory:
                        if "flint" not in inventory:
                            return "mine 10 gravel"
                        else:
                            return "craft flint_and_steel"
    else:
        if "crafting_table" in inventory:
            if "oak_log" in inventory:
                return "create oak_planks now"
            if "stick" in inventory:
                return "create wooden_pickaxe now"
            else:
                return "create 18 times stick now"
        else:
            if "oak_log" in inventory:
                return "create oak_planks now"
            else:
                if "oak_planks" in inventory:
                    return "craft crafting_table now"
                return "collect oak_log"
