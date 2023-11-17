import assert from "assert";
import pathfinderModule from "mineflayer-pathfinder";

import { Arg } from "../arg.js";
import { Bot } from "../bot.js";
import { doArgArrayMatchParameterArray, Parameter } from "../parameter.js";

import { ActionInstance } from "./action_instance.js";

const ACTION_NAME = "PlaceBlock";

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
];

export class PlaceBlockActionInstance extends ActionInstance {
  private readonly x: number;
  private readonly y: number;
  private readonly z: number;
  private readonly blockName: string;

  private onGoalReachedBound = this.onGoalReached.bind(this);
  private onPathUpdateBound = this.onPathUpdate.bind(this);

  constructor(id: string, args: ReadonlyArray<Arg>, bot: Bot) {
    super(id, ACTION_NAME, args, bot);

    if (doArgArrayMatchParameterArray(args, PARAMETERS) === false) {
      throw new Error("args do not match parameters");
    }

    this.x = this.args["x"].value as number;
    this.y = this.args["y"].value as number;
    this.z = this.args["z"].value as number;
    this.blockName = this.args["blockName"].value as string;
  }

  override get canPause(): boolean {
    return true;
  }

  override async cancelRun(): Promise<void> {
    await this.stopPathfinding();
  }

  override async pauseRun(): Promise<void> {
    await this.stopPathfinding();
  }

  override async resumeRun(): Promise<void> {
    await this.startPathfinding();
  }

  override async startRun(): Promise<void> {
    await this.startPathfinding();
  }

  private async onGoalReached(): Promise<void> {
    await this.stopPathfinding();

    return this.succeed();
  }

  private async onPathUpdate(result: { status: string }): Promise<void> {
    if (result.status !== "noPath" && result.status !== "timeout") {
      return;
    }

    let reason: string;
    switch (result.status) {
      case "noPath":
        reason = "cannot find a path to the goal";
        break;

      case "timeout":
        reason = "take too long to find a path to the goal";
        break;

      default:
        assert.fail("unreachable");
    }

    await this.stopPathfinding();

    return this.fail(reason);
  }

  private async startPathfinding(): Promise<void> {
    if (
      this.onGoalReachedBound !== undefined ||
      this.onPathUpdateBound !== undefined
    ) {
      throw new Error("pathfinding already started");
    }

    const goal = new pathfinderModule.goals.GoalBlock(this.x, this.y, this.z);
    this.bot.mineflayerBot.pathfinder.setGoal(goal);

    this.bot.mineflayerBot.on("goal_reached", this.onGoalReachedBound);
    this.bot.mineflayerBot.on("path_update", this.onPathUpdateBound);
  }

  private async stopPathfinding(): Promise<void> {
    if (
      this.onGoalReachedBound === undefined ||
      this.onPathUpdateBound === undefined
    ) {
      throw new Error("pathfinding not started");
    }

    this.bot.mineflayerBot.off("goal_reached", this.onGoalReachedBound);
    this.bot.mineflayerBot.off("path_update", this.onPathUpdateBound);

    this.bot.mineflayerBot.pathfinder.setGoal(null);
  }
}
