import {Arg} from '../arg.js';
import {Bot} from '../bot.js';
import {Parameter} from '../parameter.js';

import {ActionInstance} from './action_instance.js';
import {GoToActionInstance} from './go_to_action_instance.js';
import {PredefinedAction} from './predefined_action.js';

const NAME = 'GoTo';

const DESCRIPTION = 'Go to a specific location';

const PARAMETERS: ReadonlyArray<Parameter> = [
  {
    name: 'x',
    description: 'X coordinate',
    type: 'number',
  },
  {
    name: 'y',
    description: 'Y coordinate',
    type: 'number',
  },
  {
    name: 'z',
    description: 'Z coordinate',
    type: 'number',
  },
];

export class GoToAction extends PredefinedAction {
  constructor() {
    super(NAME, DESCRIPTION, PARAMETERS);
  }

  override instantiate(id: string, args: ReadonlyArray<Arg>, bot: Bot):
      ActionInstance {
    return new GoToActionInstance(id, args, bot);
  }
}
