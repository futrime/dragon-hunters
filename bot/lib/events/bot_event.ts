import { Arg, isArgArrayDuplicate } from "../arg.js";
import {
  doArgArrayMatchParameterArray,
  isParameterArrayDuplicate,
  Parameter,
} from "../parameter.js";

export abstract class BotEvent {
  constructor(
    readonly id: string,
    readonly name: string,
    readonly description: string,
    readonly args: ReadonlyArray<Arg>,
    readonly parameters: ReadonlyArray<Parameter>,
    readonly updatedTime: Date
  ) {
    if (isArgArrayDuplicate(args)) {
      throw new Error("duplicate argument");
    }
    console.log(parameters);
    if (isParameterArrayDuplicate(parameters) === true) {
      throw new Error("parameters duplicate");
    }

    if (doArgArrayMatchParameterArray(args, parameters) === false) {
      throw new Error("args do not match parameters");
    }
  }
}
