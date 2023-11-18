import { Arg } from "../arg.js";
import { Bot } from "../bot.js";
import { Parameter } from "../parameter.js";

import { Action } from "./action.js";
import { ActionInstance } from "./action_instance.js";
import { FurnaceActionInstance } from "./furnace_action_instance.js";

const NAME = "Furnace";

const DESCRIPTION = "Furnace something";

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
    name: "inputItemName",
    description: "The name of the item to be smelted",
    type: "string",
  },
  {
    name: "inputItemCount",
    description: "The count of the item to be smelted",
    type: "number",
  },
  {
    name: "fuelName",
    description: "The name of the fuel",
    type: "string",
  },
  {
    name: "fuelCount",
    description: "The count of the fuel",
    type: "number",
  },
];

export class FurnaceAction extends Action {
  constructor() {
    super(NAME, DESCRIPTION, PARAMETERS);
  }

  override instantiate(
    id: string,
    args: ReadonlyArray<Arg>,
    bot: Bot
  ): ActionInstance {
    return new FurnaceActionInstance(id, args, bot);
  }
}
