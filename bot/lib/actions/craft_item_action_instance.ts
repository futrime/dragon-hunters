import assert from "assert";
import pathfinderModule from "mineflayer-pathfinder";
import pWaitFor from "p-wait-for";
import { Vec3 } from "vec3";

import { Arg } from "../arg.js";
import { Bot } from "../bot.js";
import { doArgArrayMatchParameterArray, Parameter } from "../parameter.js";

import { ActionInstance } from "./action_instance.js";
import { Block } from "prismarine-block";

const ACTION_NAME = "CraftItem";

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

export class CraftItemActionInstance extends ActionInstance {
  private readonly itemName: string;
  private readonly count: number;
  private readonly craftingTableX: number;
  private readonly craftingTableY: number;
  private readonly craftingTableZ: number;

  private readonly MaxCraftingTableDisdance = 32;

  constructor(id: string, args: ReadonlyArray<Arg>, bot: Bot) {
    super(id, ACTION_NAME, args, bot);

    if (doArgArrayMatchParameterArray(args, PARAMETERS) === false) {
      throw new Error("args do not match parameters");
    }

    this.itemName = this.args["itemName"].value as string;
    this.count = this.args["count"].value as number;
    this.craftingTableX = this.args["craftingTableX"].value as number;
    this.craftingTableY = this.args["craftingTableY"].value as number;
    this.craftingTableZ = this.args["craftingTableZ"].value as number;
  }

  override async cancelRun(): Promise<void> {}

  override async pauseRun(): Promise<void> {}

  override async resumeRun(): Promise<void> {}

  override async startRun(): Promise<void> {
    this.runCraftItem();
  }

  private async runCraftItem(): Promise<void> {
    // const position = this.bot.mineflayerBot.entity.position;

    const craftingTable: Block | null = this.bot.mineflayerBot.blockAt(
      new Vec3(this.craftingTableX, this.craftingTableY, this.craftingTableZ)
    );

    if (craftingTable === null || craftingTable.name !== "crafting_table") {
      this.fail("Target block is not a crafting table!");
    }

    const itemByName = this.bot.mcdata.itemsByName[this.itemName];
    if (itemByName === undefined) {
      this.fail("Item to be crafted not found!");
    }
    console.log(craftingTable);

    const recipe = this.bot.mineflayerBot.recipesFor(
      itemByName.id,
      null,
      1,
      craftingTable
    )[0];

    this.bot.mineflayerBot.craft(recipe, this.count, craftingTable!);
  }
}