import pvp from "mineflayer-pvp";

import assert from "assert";

import { Arg } from "../arg.js";
import { Bot } from "../bot.js";
import { doArgArrayMatchParameterArray, Parameter } from "../parameter.js";

import { ActionInstance } from "./action_instance.js";
import { Entity } from "prismarine-entity";

const ACTION_NAME = "KillMob";

const PARAMETERS: ReadonlyArray<Parameter> = [
  {
    name: "mobId",
    description: "Id of the mob",
    type: "number",
  },
];

export class KillMobActionInstance extends ActionInstance {
  private readonly mobId: number;

  constructor(id: string, args: ReadonlyArray<Arg>, bot: Bot) {
    super(id, ACTION_NAME, args, bot);

    if (doArgArrayMatchParameterArray(args, PARAMETERS) === false) {
      throw new Error("args do not match parameters");
    }

    this.mobId = this.args["mobId"].value as number;
  }

  override get canPause(): boolean {
    return false;
  }

  override async cancelRun(): Promise<void> {}

  override async pauseRun(): Promise<void> {
    throw new Error(`cannot pause ${this.actionName} instance`);
  }

  override async resumeRun(): Promise<void> {
    throw new Error(`cannot resume ${this.actionName} instance`);
  }

  override async startRun(): Promise<void> {
    // wait for next tick to guarantee that the job is ready
    setImmediate(() => {
      this.startKillingMob();
    });
  }

  private async startKillingMob(): Promise<void> {
    try {
      const mob: Entity = this.bot.mineflayerBot.entities[this.mobId];
      if (mob === undefined) {
        return this.fail(`mob with id ${this.mobId} not found`);
      }
      await this.bot.mineflayerBot.pvp.attack(mob);

      return this.succeed();
    } catch (error) {
      assert(error instanceof Error);
      return this.fail(error.message);
    }
  }
}
