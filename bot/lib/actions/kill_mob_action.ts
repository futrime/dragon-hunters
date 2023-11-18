import { Arg } from "../arg.js";
import { Bot } from "../bot.js";
import { Parameter } from "../parameter.js";

import { Action } from "./action.js";
import { ActionInstance } from "./action_instance.js";
import { KillMobActionInstance } from "./kill_mob_action_instance.js";

const NAME = "KillMob";

const DESCRIPTION = "Kill a mob";

const PARAMETERS: ReadonlyArray<Parameter> = [
  {
    name: "mobId",
    description: "Id of the mob",
    type: "number",
  }
];

export class KillMobAction extends Action {
  constructor() {
    super(NAME, DESCRIPTION, PARAMETERS);
  }

  override instantiate(
    id: string,
    args: ReadonlyArray<Arg>,
    bot: Bot
  ): ActionInstance {
    return new KillMobActionInstance(id, args, bot);
  }
}
