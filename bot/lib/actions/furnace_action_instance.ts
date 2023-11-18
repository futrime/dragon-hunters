import assert from "assert";
import { Vec3 } from "vec3";

import { Arg } from "../arg.js";
import { Bot } from "../bot.js";
import { doArgArrayMatchParameterArray, Parameter } from "../parameter.js";

import { ActionInstance } from "./action_instance.js";

const ACTION_NAME = "Furnace";

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

export class FurnaceActionInstance extends ActionInstance {
  private readonly x: number;
  private readonly y: number;
  private readonly z: number;
  private readonly inputItemName: string;
  private readonly inputItemCount: number;
  private readonly fuelName: string;
  private readonly fuelCount: number;

  constructor(id: string, args: ReadonlyArray<Arg>, bot: Bot) {
    super(id, ACTION_NAME, args, bot);

    if (doArgArrayMatchParameterArray(args, PARAMETERS) === false) {
      throw new Error("args do not match parameters");
    }

    this.x = this.args["x"].value as number;
    this.y = this.args["y"].value as number;
    this.z = this.args["z"].value as number;
    this.inputItemName = this.args["inputItemName"].value as string;
    this.inputItemCount = this.args["inputItemCount"].value as number;
    this.fuelName = this.args["fuelName"].value as string;
    this.fuelCount = this.args["fuelCount"].value as number;
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
      this.startFurnacing();
    });
  }

  private async startFurnacing(): Promise<void> {
    try {
      // Check if the input item is in the inventory
      const inputItem = this.bot.mineflayerBot.inventory
        .items()
        .find((item) => {
          return item.name === this.inputItemName;
        });
      // If the input item is not in the inventory, throw an error
      if (!inputItem) {
        return this.fail(
          `Input item ${this.inputItemName} is not in the inventory`
        );
      }
      if (inputItem.count < this.inputItemCount) {
        return this.fail(
          `Fuel ${this.inputItemName} is not enough in the inventory`
        );
      }

      // Check if the fuel is in the inventory
      const fuel = this.bot.mineflayerBot.inventory.items().find((item) => {
        return item.name === this.fuelName;
      });
      // If the fuel is not in the inventory, throw an error
      if (!fuel) {
        return this.fail(`Fuel ${this.fuelName} is not in the inventory`);
      }
      if (fuel.count < this.fuelCount) {
        return this.fail(
          `Fuel ${this.fuelName} is not enough in the inventory`
        );
      }

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
      // Check if the furnace is empty
      if (!furnace.inputItem() || !furnace.fuelItem()) {
        return this.fail(
          `Furnace at (${this.x}, ${this.y}, ${this.z}) is not empty`
        );
      }

      // Put the input item into the furnace
      await furnace.putInput(inputItem.type, null, this.inputItemCount);
      // Put the input fuel into the furnace
      await furnace.putFuel(fuel.type, null, this.fuelCount);

      // // Wait for the furnace to finish
      // await new Promise((resolve) => {
      //   furnace.once("close", () => {
      //     resolve();
      //   });
      // });
    } catch (error) {
      assert(error instanceof Error);
      return this.fail(error.message);
    }
  }
}
