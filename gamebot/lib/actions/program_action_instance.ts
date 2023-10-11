import assert from 'assert';
import consola from 'consola';

import {Arg} from '../arg.js';
import {Bot} from '../bot.js';
import {doArgArrayMatchParameterArray, isParameterArrayDuplicate} from '../parameter.js';
import {ActionInvocation} from '../programs/action_invocation.js';
import {Program} from '../programs/program.js';

import {ActionInstance} from './action_instance.js';
import {ActionInstanceState} from './action_instance_state.js';
import {ParameterWithVariable} from './parameter_with_variable.js';

export class ProgramActionInstance extends ActionInstance {
  private readonly variables: Record<string, unknown> = {};

  private currentActionInstance?: ActionInstance = undefined;
  private shouldCancel: boolean = false;
  private shouldPause: boolean = false;

  constructor(
      id: string, args: ReadonlyArray<Arg>, bot: Bot, actionName: string,
      parameters: ReadonlyArray<ParameterWithVariable>,
      private readonly program: Program) {
    super(id, actionName, args, bot);

    if (isParameterArrayDuplicate(parameters) === false) {
      throw new Error('parameters duplicate');
    }

    if (doArgArrayMatchParameterArray(args, parameters) === false) {
      throw new Error('args do not match parameters');
    }

    // Set variables
    for (const parameter of parameters) {
      // Variable should start with $
      if (!parameter.variable.startsWith('$')) {
        throw new Error(`variable ${parameter.variable} should start with $`);
      }

      this.variables[parameter.variable] = this.args[parameter.name].value;
    }
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

  private createActionInstanceFromActionInvocation(
      actionInvocation: ActionInvocation): ActionInstance {
    const action = this.bot.getAction(actionInvocation.action);

    if (action === undefined) {
      throw new Error(`action ${actionInvocation.action} does not exist`);
    }

    const args = actionInvocation.args.map((arg) => {
      if (typeof arg.value === 'string' && arg.value.startsWith('$')) {
        const value = this.variables[arg.value];

        return {
          ...arg,
          value,
        };
      }

      return arg;
    });

    const actionInstance = action.instantiate('', args, this.bot);

    return actionInstance;
  }

  private async evaluate() {
    for (const actionInvocation of this.program) {
      const actionInstance =
          this.createActionInstanceFromActionInvocation(actionInvocation);

      assert(this.currentActionInstance === undefined);
      this.currentActionInstance = actionInstance;

      await actionInstance.start();

      // Should check whenever other coroutine may cancel this action instance.
      if (this.shouldCancel) {
        return;
      }

      if (this.shouldPause) {
        await this.waitTillShouldPauseBecomesFalse();
      }

      await this.waitTillActionInstanceEnd(actionInstance);

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
