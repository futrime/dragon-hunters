import { Arg } from "../arg.js";
import { Bot } from "../bot.js";
import { Parameter } from "../parameter.js";

import { Action } from "./action.js";
import { ActionInstance } from "./action_instance.js";
import { PlaceBlockActionInstance } from "./place_block_action_instance.js";

const NAME = "PlaceBlock";

const DESCRIPTION = "Place a block";

const PARAMETERS: ReadonlyArray<Parameter> = [
  {
    name: "x",
    description: "X coordinate",
    type: "number",
  },
  {
    name: "y",
    description: "Y coordinate",
    type: "number",
  },
  {
    name: "z",
    description: "Z coordinate",
    type: "number",
  },
  {
    name: "blockName",
    description: "The name of the block",
    type: "string",
  },
];

export class PlaceBlockAction extends Action {
  constructor() {
    super(NAME, DESCRIPTION, PARAMETERS);
  }

  override instantiate(
    id: string,
    args: ReadonlyArray<Arg>,
    bot: Bot
  ): ActionInstance {
    return new PlaceBlockActionInstance(id, args, bot);
  }
}
