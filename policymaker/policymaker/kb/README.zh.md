# EdK Knowledge Base

The knowledge base containing related knowledge of Minecraft.

## 开发进度

2023.9.25 添加了无固定顺序合成表查询

2023.9.26 添加了固定顺序合成表查询

2023.9.26 修复了迭代 tag 的问题

2023.9.26 修复了 xx_from_xx 类型的多版本合成表的问题

2023.9.26 增加了熔炉合成表的查询

2023.9.26 增加了怪物掉落表的查询

2023.10.4 增加了方块掉落及挖掘条件的查询

2023.10.5 增加了临时的 qa

## 基本使用示例

```python
import knowledge_base as kblib

kb = kblib.KnowledgeBase()
print(kb.crafted_to_material["diamond"])
print(kb.material_to_crafted["diamond"])

kb.add_qa("Where can I get diamond?", "mining diamond ore")
kb.add_qa("What can I do with diamond?", "crafting diamond pickaxe")
qa_result = kb.get_qa("diamond")
print(qa_result)
```
>输出 1：`[{'recipe': {'diamond_block': 1}, 'type': 'player'}, {'recipe': {'de epslate_diamond_ore': 1}, 'type': 'furnace'}, {'recipe': {'diamond_ore': 1}, 'type': 'furnace'}, {'recipe': {'deepslate_diamond_ore': 1}, 'type': 'mine', 'condition': 'tool: pickaxe better than iron'}, {'recipe': {'diamond_ore': 1}, 'type': 'mine', 'condition': 'tool: pickaxe better than iron'}]`
>
>输出 2：`[{'item': 'diamond_axe', 'type': 'crafting_table'}, {'item': 'diamond_block', 'type': 'crafting_table'}, {'item': 'diamond_boots', 'type': 'crafting_table'}, {'item': 'diamond_chestplate', 'type': 'crafting_table'}, {'item': 'diamond_helmet', 'type': 'crafting_table'}, {'item': 'diamond_hoe', 'type': 'crafting_table'}, {'item': 'diamond_leggings', 'type': 'crafting_table'}, {'item': 'diamond_pickaxe', 'type': 'crafting_table'}, {'item': 'diamond_shovel', 'type': 'crafting_table'}, {'item': 'diamond_sword', 'type': 'crafting_table'}, {'item': 'enchanting_table', 'type': 'crafting_table'}, {'item': 'jukebox', 'type': 'crafting_table'}]`
>
>输出 3：`{'Where can I get diamond?': 'mining diamond ore', 'What can I do with diamond?': 'crafting diamond pickaxe'}`

## 使用方法详解

### `crafted_to_material`

`crafted_to_material` 是一个字典，键为合成物品，值是一个列表，列表中的每个元素都是一个字典，字典中包含了合成的原材料，合成的类型，以及条件（如果有的话）。

### `material_to_crafted`

`material_to_crafted` 是一个字典，键为原材料，值是一个列表，列表中的每个元素都是一个字典，字典中包含了原材料的合成物品，合成的类型，以及条件（如果有的话）。

### `add_qa` 和 `get_qa`

`add_qa` 用于添加一个问题及其答案，`get_qa` 用于获取一个问题的答案。`add_qa` 的第一个参数是问题，第二个参数是答案。`get_qa` 的参数是想要查找的关键字，返回值是一个字典，键为问题，值为答案。

### 合成类型

现在有 `player`（使用 4x4 合成表合成）、`crafting_table`（使用 3x3 合成表合成）、`furnace`（使用熔炉烧制）、`mine`（挖掘方块掉落）、`combat`（战斗怪物掉落）五种合成类型。

### 条件

目前只有挖掘有条件，条件主要有 `table_bonus`（随机掉落）、`tool`（工具限制，包括但不限于“精准采集”“使用比石镐更好的镐子”等）

## 已知问题

~~对于迭代 tag 的存在暂时没有处理。~~ 已经解决。

~~对于 xx_from_xx 类型的多版本合成表暂时未处理。~~ 已经解决。

对于 barrel、campfire、soul_campfire 暂时无法处理。现在是使用 hard code 直接屏蔽掉
