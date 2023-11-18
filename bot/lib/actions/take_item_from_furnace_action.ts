import { Arg } from "../arg.js";
import { Bot } from "../bot.js";
import { Parameter } from "../parameter.js";

import { Action } from "./action.js";
import { ActionInstance } from "./action_instance.js";
import { TakeItemFromFurnaceActionInstance } from "./take_item_from_furnace_action_instance.js";

const NAME = "TakeItemsFromFurnace";

const DESCRIPTION = "Take some items from the target furnace";

const PARAMETERS: ReadonlyArray<Parameter> = [
  {
    name: "x",
    description: "X coordinate of the furnace",
    type: "number",
  },
  {
    name: "y",
    description: "Y coordinate of the furnace",
    type: "number",
  },
  {
    name: "z",
    description: "Z coordinate of the furnace",
    type: "number",
  },
  {
    name: "itemType",
    description:
      "The type of the item to be taken which can be 'input' or 'fuel' or 'output'",
    type: "string",
  }
];

export class TakeItemFromFurnaceAction extends Action {
  constructor() {
    super(NAME, DESCRIPTION, PARAMETERS);
  }

  override instantiate(
    id: string,
    args: ReadonlyArray<Arg>,
    bot: Bot
  ): ActionInstance {
    return new TakeItemFromFurnaceActionInstance(id, args, bot);
  }
}
