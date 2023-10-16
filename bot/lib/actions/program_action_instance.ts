import {Arg} from '../arg.js';
import {Bot} from '../bot.js';
import {ActionInvocation} from '../programs/action_invocation.js';
import {Program} from '../programs/program.js';
import {createProgram} from '../programs/program_creation.js';

import {ActionInstance} from './action_instance.js';
import {CompositeActionInstance} from './composite_action_instance.js';
import {ParameterWithVariable} from './parameter_with_variable.js';

export class ProgramActionInstance extends CompositeActionInstance {
  private readonly program: Program;

  constructor(
      id: string, args: ReadonlyArray<Arg>, bot: Bot, actionName: string,
      parameters: ReadonlyArray<ParameterWithVariable>, programJson: object) {
    super(id, actionName, args, bot, parameters);

    // Set variables
    const variables: Record<string, unknown> = {};
    for (const parameter of parameters) {
      // Variable should start with $
      if (!parameter.variable.startsWith('$')) {
        throw new Error(`variable ${parameter.variable} should start with $`);
      }

      variables[parameter.variable] = this.args[parameter.name].value;
    }

    // Replace variables in programJson
    const modifiedProgramJson =
        JSON.parse(JSON.stringify(programJson, (_, value) => {
          for (const variable of Object.keys(variables)) {
            if (value === variable) {
              return variables[variable];
            }
          }
        }));

    this.program = createProgram(modifiedProgramJson);
  }

  private createActionInstance(actionInvocation: ActionInvocation):
      ActionInstance {
    const action = this.bot.getAction(actionInvocation.action);
    if (action === undefined) {
      throw new Error(`action ${actionInvocation.action} not found`);
    }

    const actionInstance =
        action.instantiate('', actionInvocation.args, this.bot);

    return actionInstance;
  }

  protected override * generateActionInstance(): Generator<ActionInstance> {
    for (const actionInvocation of this.program) {
      yield this.createActionInstance(actionInvocation);
    }
  }
}
