import assert from "assert";
import pathfinderModule from "mineflayer-pathfinder";
import { Vec3 } from "vec3";

import { Arg } from "../arg.js";
import { Bot } from "../bot.js";
import { doArgArrayMatchParameterArray, Parameter } from "../parameter.js";

import { ActionInstance } from "./action_instance.js";

const ACTION_NAME = "PlaceBlock";

const PARAMETERS: ReadonlyArray<Parameter> = [
  {
    name: "x",
    description: "X coordinate of the block you want to place",
    type: "number",
  },
  {
    name: "y",
    description: "Y coordinate of the block you want to place",
    type: "number",
  },
  {
    name: "z",
    description: "Z coordinate of the block you want to place",
    type: "number",
  },
  {
    name: "blockName",
    description: "The name of the block",
    type: "string",
  },
];

export class PlaceBlockActionInstance extends ActionInstance {
  private readonly x: number;
  private readonly y: number;
  private readonly z: number;
  private readonly blockName: string;

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
      this.startPlacingBlock();
    });
  }

  private async startPlacingBlock(): Promise<void> {
    try {
      // Check if the block is in the inventory
      const block = this.bot.mineflayerBot.inventory.items().find((item) => {
        return item.name === this.blockName;
      });
      // If the block is not in the inventory, throw an error
      if (!block) {
        return this.fail("Block not found in inventory");
      }

      // Swap the block to the main hand
      await this.bot.mineflayerBot.equip(block, "hand");

      // Place the block
      // Tranverse 6 faces of the target position
      const directions: Array<Vec3> = [
        new Vec3(1, 0, 0),
        new Vec3(-1, 0, 0),
        new Vec3(0, 1, 0),
        new Vec3(0, -1, 0),
        new Vec3(0, 0, 1),
        new Vec3(0, 0, -1),
      ];

      for (let i: number = 0; i < directions.length; i++) {
        const direction = directions[i];

        const neighborBlock = this.bot.mineflayerBot.blockAt(
          new Vec3(this.x, this.y, this.z).plus(direction)
        );

        const reverseDirection = direction.scaled(-1);

        if (neighborBlock && neighborBlock.name !== "air") {
          // Look at the middle of the neighbor block (deprecated: no need to look at the block)
          // await this.bot.mineflayerBot.lookAt(
          //   neighborBlock.position.plus(reverseDirection.scaled(0.5))
          // );

          // Place block
          await this.bot.mineflayerBot.placeBlock(
            neighborBlock,
            reverseDirection
          );

          // // TEST: Build a block wall
          // for (let y = 0; y < 20; y++) {
          //   const block = this.bot.mineflayerBot.blockAt(
          //     neighborBlock.position.offset(0, y, 0)
          //   );
          //   console.log(block?.position);
          //   if (block !== null)
          //     await this.bot.mineflayerBot.placeBlock(block, new Vec3(0, 1, 0));
          // }

          // // TEST: Build a nether door
          // await this.bot.mineflayerBot.placeBlock(
          //   neighborBlock,
          //   reverseDirection
          // );
          // for (let x = 0; x <= 2; x++) {
          //   const block = this.bot.mineflayerBot.blockAt(
          //     neighborBlock.position.offset(x, 1, 0)
          //   );
          //   console.log(block?.position);
          //   if (block !== null)
          //     await this.bot.mineflayerBot.placeBlock(block, new Vec3(1, 0, 0));
          // }

          // for (let y = 0; y <= 3; y++) {
          //   const block = this.bot.mineflayerBot.blockAt(
          //     neighborBlock.position.offset(0, y + 1, 0)
          //   );
          //   console.log(block?.position);
          //   if (block !== null)
          //     await this.bot.mineflayerBot.placeBlock(block, new Vec3(0, 1, 0));
          // }

          // for (let x = 0; x <= 2; x++) {
          //   const block = this.bot.mineflayerBot.blockAt(
          //     neighborBlock.position.offset(x, 5, 0)
          //   );
          //   console.log(block?.position);
          //   if (block !== null)
          //     await this.bot.mineflayerBot.placeBlock(block, new Vec3(1, 0, 0));
          // }

          // for (let y = 0; y <= 2; y++) {
          //   const block = this.bot.mineflayerBot.blockAt(
          //     neighborBlock.position.offset(3, y + 1, 0)
          //   );
          //   console.log(block?.position);
          //   if (block !== null)
          //     await this.bot.mineflayerBot.placeBlock(block, new Vec3(0, 1, 0));
          // }

          // // swap the flint and steel to the main hand
          // const flintAndSteel = this.bot.mineflayerBot.inventory
          //   .items()
          //   .find((item) => {
          //     return item.name === "flint_and_steel";
          //   });
          // if (!flintAndSteel) {
          //   return this.fail("Flint and steel not found in inventory");
          // }
          // await this.bot.mineflayerBot.equip(flintAndSteel, "hand");

          // // light the portal
          // await this.bot.mineflayerBot.placeBlock(
          //   this.bot.mineflayerBot.blockAt(
          //     neighborBlock.position.offset(1, 1, 0)
          //   )!,
          //   new Vec3(0, 1, 0)
          // );

          return this.succeed();
        }
      }
      return this.fail(
        `Block ${this.blockName} cannot be placed at (${this.x}, ${this.y}, ${this.z})`
      );
    } catch (error) {
      assert(error instanceof Error);
      return this.fail(error.message);
    }
  }
}
