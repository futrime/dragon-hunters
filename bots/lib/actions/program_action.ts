import {Arg} from '../arg.js';
import {Bot} from '../bot.js';
import {Program} from '../programs/program.js';

import {Action} from './action.js';
import {ActionInstance} from './action_instance.js';
import {ParameterWithVariable} from './parameter_with_variable.js';
import {ProgramActionInstance} from './program_action_instance.js';

export class ProgramAction extends Action {
  private readonly parametersWithVariable: ReadonlyArray<ParameterWithVariable>;

  constructor(
      name: string, description: string,
      parameters: ReadonlyArray<ParameterWithVariable>,
      private readonly program: Program) {
    super(name, description, parameters);

    this.parametersWithVariable = parameters;
  }

  override instantiate(id: string, args: readonly Arg[], bot: Bot):
      ActionInstance {
    return new ProgramActionInstance(
        id, args, bot, this.name, this.parametersWithVariable, this.program);
  }
}
