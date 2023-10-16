import assert from 'assert';

import {Arg} from '../arg.js';
import {Bot} from '../bot.js';
import {Parameter} from '../parameter.js';

import {ActionInstance} from './action_instance.js';
import {CompositeActionInstance} from './composite_action_instance.js';

const ACTION_NAME = 'ExploreUntil';

const DISTANCE_TRAVELED_PER_STEP = 32;

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

export class ExploreUntilActionInstance extends CompositeActionInstance {
  private readonly x: number;
  private readonly y: number;
  private readonly z: number;
  private readonly timeout: number;

  private timer?: NodeJS.Timeout = undefined;

  constructor(id: string, args: ReadonlyArray<Arg>, bot: Bot) {
    super(id, ACTION_NAME, args, bot, PARAMETERS);

    // Depends on GoToAction
    if (bot.getAction('GoTo') === undefined) {
      throw new Error('cannot find dependency GoToAction');
    }

    this.x = this.args['x'].value as number;
    this.y = this.args['y'].value as number;
    this.z = this.args['z'].value as number;
    this.timeout = this.args['timeout'].value as number;

    // Normalize direction vector
    const length =
        Math.sqrt(this.x * this.x + this.y * this.y + this.z * this.z);
    this.x /= length;
    this.y /= length;
    this.z /= length;
  }

  protected override async afterRun(): Promise<void> {
    assert.notStrictEqual(
        this.timer, undefined, 'timer should not be empty here');
    clearTimeout(this.timer);
  }

  protected override async cancelRun(): Promise<void> {
    assert.notStrictEqual(
        this.timer, undefined, 'timer should not be empty here');
    clearTimeout(this.timer);

    await super.cancelRun();
  }

  protected override async startRun(): Promise<void> {
    await super.startRun();

    assert.strictEqual(
        this.timer, undefined,
        'timer should be undefined before starting the action instance');

    this.timer =
        setTimeout(this.cancelRun.bind(this) as (() => void), this.timeout);
  }

  protected override * generateActionInstance(): Generator<ActionInstance> {
    const goToAction = this.bot.getAction('GoTo');
    assert.notStrictEqual(
        goToAction, undefined, 'GoToAction should not be undefined');

    const startTime = Date.now();

    while (Date.now() - startTime < this.timeout) {
      yield goToAction!.instantiate(
          '',
          [
            {name: 'x', value: this.x * DISTANCE_TRAVELED_PER_STEP},
            {name: 'y', value: this.y * DISTANCE_TRAVELED_PER_STEP},
            {name: 'z', value: this.z * DISTANCE_TRAVELED_PER_STEP}
          ],
          this.bot);
    }
  }
}
