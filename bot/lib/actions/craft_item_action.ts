import { Arg } from "../arg.js";
import { Bot } from "../bot.js";
import { Parameter } from "../parameter.js";

import { Action } from "./action.js";
import { ActionInstance } from "./action_instance.js";
import { CraftItemActionInstance } from "./craft_item_action_instance.js";

const NAME = "CraftItem";

const DESCRIPTION = "Craft an item";

const PARAMETERS: ReadonlyArray<Parameter> = [
  {
    name: "itemName",
    description: "The name of the item",
    type: "string",
  },
  {
    name: "count",
    description: "The count of the item",
    type: "number",
  },
  {
    name: "craftingTableX",
    description: "The X coordinate of the target crafting table",
    type: "number",
  },
  {
    name: "craftingTableY",
    description: "The Y coordinate of the target crafting table",
    type: "number",
  },
  {
    name: "craftingTableZ",
    description: "The Z coordinate of the target crafting table",
    type: "number",
  },
];

export class CraftItemAction extends Action {
  constructor() {
    super(NAME, DESCRIPTION, PARAMETERS);
  }

  override instantiate(
    id: string,
    args: ReadonlyArray<Arg>,
    bot: Bot
  ): ActionInstance {
    return new CraftItemActionInstance(id, args, bot);
  }
}
