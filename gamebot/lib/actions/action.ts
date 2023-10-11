import {Arg} from '../arg.js';
import {Bot} from '../bot.js';
import {isParameterArrayDuplicate, Parameter} from '../parameter.js';

import {ActionInstance} from './action_instance.js';

export abstract class Action {
  readonly parameters: Record<string, Parameter>;

  constructor(
      readonly name: string, readonly description: string,
      parameters: ReadonlyArray<Parameter>) {
    if (isParameterArrayDuplicate(parameters)) {
      throw new Error('duplicate parameter');
    }

    this.parameters = {};
    for (const parameter of parameters) {
      this.parameters[parameter.name] = parameter;
    }
  }

  /**
   * Instantiates an action instance.
   * @param id The action instance ID.
   * @param args The action instance arguments.
   * @param bot The bot.
   * @returns The action instance.
   */
  abstract instantiate(id: string, args: ReadonlyArray<Arg>, bot: Bot):
      ActionInstance;
}
