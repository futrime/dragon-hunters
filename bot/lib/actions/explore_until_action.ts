import {Arg} from '../arg.js';
import {Bot} from '../bot.js';
import {Parameter} from '../parameter.js';

import {Action} from './action.js';
import {ActionInstance} from './action_instance.js';
import {ExploreUntilActionInstance} from './explore_until_action_instance.js';

const NAME = 'ExploreUntil';

const DESCRIPTION = 'Explore until timeout';

const PARAMETERS: ReadonlyArray<Parameter> = [
  {
    name: 'x',
    description: 'X coordinate of the direction vector',
    type: 'number',
  },
  {
    name: 'y',
    description: 'Y coordinate of the direction vector',
    type: 'number',
  },
  {
    name: 'z',
    description: 'Z coordinate of the direction vector',
    type: 'number',
  },
  {
    name: 'timeout',
    description: 'Timeout in milliseconds',
    type: 'number',
  },
];

export class ExploreUntilAction extends Action {
  constructor() {
    super(NAME, DESCRIPTION, PARAMETERS);
  }

  override instantiate(id: string, args: ReadonlyArray<Arg>, bot: Bot):
      ActionInstance {
    return new ExploreUntilActionInstance(id, args, bot);
  }
}
