import assert from "assert";
import { Vec3 } from "vec3";

import { Arg } from "../arg.js";
import { Bot } from "../bot.js";
import { doArgArrayMatchParameterArray, Parameter } from "../parameter.js";

import { ActionInstance } from "./action_instance.js";

const ACTION_NAME = "TakeItemsFromFurnace";

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
  },
];

export class TakeItemFromFurnaceActionInstance extends ActionInstance {
  private readonly x: number;
  private readonly y: number;
  private readonly z: number;
  private readonly itemType: string;

  constructor(id: string, args: ReadonlyArray<Arg>, bot: Bot) {
    super(id, ACTION_NAME, args, bot);

    if (doArgArrayMatchParameterArray(args, PARAMETERS) === false) {
      throw new Error("args do not match parameters");
    }

    this.x = this.args["x"].value as number;
    this.y = this.args["y"].value as number;
    this.z = this.args["z"].value as number;
    this.itemType = this.args["itemType"].value as string;
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
      this.startTakingItemFromFurnace();
    });
  }

  private async startTakingItemFromFurnace(): Promise<void> {
    try {
      // Find the furnace according to (x,y,z)
      const furnaceBlock = this.bot.mineflayerBot.blockAt(
        new Vec3(this.x, this.y, this.z)
      );
      // If the furnace is not found, throw an error
      if (!furnaceBlock) {
        return this.fail(
          `Furnace is not found at (${this.x}, ${this.y}, ${this.z})`
        );
      }
      // If the furnace is not a furnace, throw an error
      if (furnaceBlock.name !== "furnace") {
        return this.fail(
          `Block at (${this.x}, ${this.y}, ${this.z}) is not a furnace`
        );
      }

      // Try to open the furnace
      const furnace = await this.bot.mineflayerBot.openFurnace(furnaceBlock);
      // If the furnace is not opened, throw an error
      if (!furnace) {
        return this.fail(
          `Furnace at (${this.x}, ${this.y}, ${this.z}) is busy`
        );
      }
      switch (this.itemType) {
        case "input":
          // Check if the input in the furnace is empty
          const inputItem = furnace.inputItem();
          if (null === inputItem) {
            return this.fail(
              `Input in the furnace at (${this.x}, ${this.y}, ${this.z}) is empty`
            );
          }
          // Try to take the input
          await furnace.takeInput();
          break;
        case "output":
          // Check if the output in the furnace is empty
          const outputItem = furnace.outputItem();
          if (null === outputItem) {
            return this.fail(
              `Output in the furnace at (${this.x}, ${this.y}, ${this.z}) is empty`
            );
          }
          // Try to take the output
          await furnace.takeOutput();
          break;
        case "fuel":
          // Check if the fuel in the furnace is empty
          const fuelItem = furnace.fuelItem();
          if (null === fuelItem) {
            return this.fail(
              `Fuel in the furnace at (${this.x}, ${this.y}, ${this.z}) is empty`
            );
          }
          // Try to take the fuel
          await furnace.takeFuel();
          break;
        default:
          return this.fail(`Item type ${this.itemType} is not supported`);
      }

      return this.succeed();
    } catch (error) {
      assert(error instanceof Error);
      return this.fail(error.message);
    }
  }
}
