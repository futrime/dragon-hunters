import assert from 'assert';
import consola from 'consola';

import {Arg} from '../arg.js';
import {Bot} from '../bot.js';
import {doArgArrayMatchParameterArray, Parameter} from '../parameter.js';

import {ActionInstance} from './action_instance.js';
import {ActionInstanceState} from './action_instance_state.js';
import {PredefinedActionInstance} from './predefined_action_instance.js';

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

export class ExploreUntilActionInstance extends PredefinedActionInstance {
  private readonly x: number;
  private readonly y: number;
  private readonly z: number;
  private readonly timeout: number;

  private currentActionInstance?: ActionInstance = undefined;
  private shouldCancel: boolean = false;
  private shouldPause: boolean = false;

  constructor(id: string, args: ReadonlyArray<Arg>, bot: Bot) {
    super(id, ACTION_NAME, args, bot);

    // Depends on GoToAction
    if (bot.getAction('GoTo') === undefined) {
      throw new Error('cannot find GoToAction');
    }

    if (doArgArrayMatchParameterArray(args, Object.values(PARAMETERS)) ===
        false) {
      throw new Error('args do not match parameters');
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

  override async cancel(): Promise<void> {
    if (this.wrappedState !== ActionInstanceState.RUNNING &&
        this.wrappedState !== ActionInstanceState.PAUSED) {
      throw new Error(
          `cannot cancel an action instance in state ${this.wrappedState}`);
    }

    this.shouldCancel = true;
    if (this.currentActionInstance !== undefined &&
        (this.currentActionInstance.state === ActionInstanceState.RUNNING ||
         this.currentActionInstance.state === ActionInstanceState.PAUSED)) {
      await this.currentActionInstance.cancel();
    }

    // Wait till the current action instance becomes undefined.
    await (() => {
      return new Promise<void>((resolve) => {
        const interval = setInterval(() => {
          if (this.currentActionInstance === undefined) {
            clearInterval(interval);
            resolve();
          }
        }, 10);
      });
    })();

    this.wrappedState = ActionInstanceState.CANCELED;
    this.eventEmitter.emit('cancel', this);
    consola.log(`${this.actionName}#${this.id} canceled`);
  }

  override async pause(): Promise<void> {
    if (this.wrappedState !== ActionInstanceState.RUNNING) {
      throw new Error(
          `cannot pause an action instance in state ${this.wrappedState}`);
    }

    this.shouldPause = true;
    if (this.currentActionInstance !== undefined &&
        this.currentActionInstance.state === ActionInstanceState.RUNNING) {
      await this.currentActionInstance.pause();
    }

    this.wrappedState = ActionInstanceState.PAUSED;
    this.eventEmitter.emit('pause', this);
    consola.log(`${this.actionName}#${this.id} paused`);
  }

  override async resume(): Promise<void> {
    if (this.wrappedState !== ActionInstanceState.PAUSED) {
      throw new Error(
          `cannot resume an action instance in state ${this.wrappedState}`);
    }

    if (this.bot.isRunningAnyJob()) {
      throw new Error('cannot resume a job because another job is running');
    }

    this.shouldPause = false;
    if (this.currentActionInstance !== undefined &&
        this.currentActionInstance.state === ActionInstanceState.PAUSED) {
      await this.currentActionInstance.resume();
    }

    this.wrappedState = ActionInstanceState.RUNNING;
    this.eventEmitter.emit('resume', this);
    consola.log(`${this.actionName}#${this.id} resumed`);
  }

  override async start(): Promise<void> {
    if (this.wrappedState !== ActionInstanceState.READY) {
      throw new Error(
          `cannot start an action instance in state ${this.wrappedState}`);
    }

    if (this.bot.isRunningAnyJob()) {
      throw new Error('cannot start a job because another job is running');
    }

    this.evaluate().catch(this.handleEvaluationError.bind(this));

    this.wrappedState = ActionInstanceState.RUNNING;
    this.eventEmitter.emit('start', this);
    consola.log(`${this.actionName}#${this.id} started`);
  }

  private async evaluate() {
    const goToAction = this.bot.getAction('GoTo');
    assert(goToAction !== undefined);

    const startTime = Date.now();

    while (Date.now() - startTime < this.timeout) {
      const goToActionInstance = goToAction.instantiate(
          '',
          [
            {name: 'x', value: this.x * DISTANCE_TRAVELED_PER_STEP},
            {name: 'y', value: this.y * DISTANCE_TRAVELED_PER_STEP},
            {name: 'z', value: this.z * DISTANCE_TRAVELED_PER_STEP}
          ],
          this.bot);

      assert(this.currentActionInstance === undefined);
      this.currentActionInstance = goToActionInstance;

      await goToActionInstance.start();

      // Should check whenever other coroutine may cancel this action instance.
      if (this.shouldCancel) {
        return;
      }

      if (this.shouldPause) {
        await this.waitTillShouldPauseBecomesFalse();
      }

      await this.waitTillActionInstanceEnd(goToActionInstance);

      // Should check whenever other coroutine may cancel this action instance.
      if (this.shouldCancel) {
        return;
      }

      if (this.shouldPause) {
        await this.waitTillShouldPauseBecomesFalse();
      }

      this.currentActionInstance = undefined;
    }

    assert(this.shouldCancel === false);

    this.wrappedState = ActionInstanceState.SUCCEEDED;
    this.eventEmitter.emit('succeed', this);
    consola.log(`${this.actionName}#${this.id} succeeded`);
  }

  private async handleEvaluationError(error: Error) {
    if (this.currentActionInstance !== undefined &&
        (this.currentActionInstance.state === ActionInstanceState.RUNNING ||
         this.currentActionInstance.state === ActionInstanceState.PAUSED)) {
      // Ignore error
      await this.currentActionInstance.cancel().catch(() => {});
    }

    this.wrappedState = ActionInstanceState.FAILED;
    this.eventEmitter.emit('fail', this, error.message);
    consola.error(`${this.actionName}#${this.id} failed: ${error.message}`);
  }

  private async waitTillActionInstanceEnd(actionInstance: ActionInstance) {
    return new Promise<void>((resolve, reject) => {
      actionInstance.eventEmitter.once('cancel', () => {
        resolve();
      });

      actionInstance.eventEmitter.once('succeed', () => {
        resolve();
      });

      actionInstance.eventEmitter.once('fail', (_, reason: string) => {
        reject(
            new Error(`action ${actionInstance.actionName} failed: ${reason}`));
      });
    });
  }

  private async waitTillShouldPauseBecomesFalse() {
    return new Promise<void>((resolve) => {
      const interval = setInterval(() => {
        if (this.shouldPause === false) {
          clearInterval(interval);
          resolve();
        }
      }, 10);
    });
  }
}
