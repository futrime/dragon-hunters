import assert from 'assert';
import pWaitFor from 'p-wait-for';

import {Arg} from '../arg.js';
import {Bot} from '../bot.js';
import {doArgArrayMatchParameterArray, isParameterArrayDuplicate, Parameter} from '../parameter.js';

import {ActionInstance} from './action_instance.js';
import {ActionInstanceState} from './action_instance_state.js';

export abstract class CompositeActionInstance extends ActionInstance {
  private currentActionInstance?: ActionInstance = undefined;

  constructor(
      id: string, actionName: string, args: ReadonlyArray<Arg>, bot: Bot,
      parameters: ReadonlyArray<Parameter>) {
    super(id, actionName, args, bot);

    if (isParameterArrayDuplicate(parameters) === false) {
      throw new Error('parameters duplicate');
    }

    if (doArgArrayMatchParameterArray(args, parameters) === false) {
      throw new Error('args do not match parameters');
    }
  }

  override get canPause(): boolean {
    return true;
  }

  protected async afterRun(): Promise<void> {
    // Do nothing
  }

  protected async beforeRun(): Promise<void> {
    // Do nothing
  }

  protected override async cancelRun(): Promise<void> {
    // this.currentActionInstance should never be undefined
    assert.notStrictEqual(
        this.currentActionInstance, undefined,
        'currentActionInstance should not be undefined');

    // Wait till RUNNING if READY
    if (this.currentActionInstance!.state === ActionInstanceState.READY) {
      await pWaitFor(
          () => this.currentActionInstance!.state ===
              ActionInstanceState.RUNNING);
    }

    if (this.currentActionInstance!.state === ActionInstanceState.RUNNING ||
        this.currentActionInstance!.state === ActionInstanceState.PAUSED) {
      await this.currentActionInstance!.cancel();
    }
  }

  protected override async pauseRun(): Promise<void> {
    // this.currentActionInstance should never be undefined
    assert.notStrictEqual(
        this.currentActionInstance, undefined,
        'currentActionInstance should not be undefined');

    await pWaitFor(() => this.currentActionInstance!.canPause === true);

    await this.currentActionInstance!.pause();
  }

  protected override async resumeRun(): Promise<void> {
    // this.currentActionInstance should never be undefined
    assert.notStrictEqual(
        this.currentActionInstance, undefined,
        'currentActionInstance should not be undefined');

    // Paused action instance can pause.
    assert.strictEqual(
        this.currentActionInstance!.canPause, true,
        'paused currentActionInstance should be able to pause');

    await this.currentActionInstance!.resume();
  }

  protected override async startRun(): Promise<void> {
    this.run().catch(this.handleRunError.bind(this));
  }

  protected abstract generateActionInstance(): Generator<ActionInstance>;

  private async handleRunError(error: Error) {
    // Pass through assertion errors
    if (error instanceof assert.AssertionError) {
      throw error;
    }

    if (this.currentActionInstance !== undefined &&
        (this.currentActionInstance.state === ActionInstanceState.RUNNING ||
         this.currentActionInstance.state === ActionInstanceState.PAUSED)) {
      await this.currentActionInstance.cancel().catch(() => {});
    }

    return this.fail(error.message);
  }

  private async run() {
    await this.beforeRun();

    for (const actionInstance of this.generateActionInstance()) {
      assert.strictEqual(
          this.currentActionInstance, undefined,
          'currentActionInstance should be undefined');

      this.currentActionInstance = actionInstance;

      await this.currentActionInstance.start();

      await this.waitTillActionInstanceEnd(this.currentActionInstance);

      this.currentActionInstance = undefined;
    }

    await this.afterRun();
  }

  private async waitTillActionInstanceEnd(actionInstance: ActionInstance) {
    return new Promise<void>((resolve) => {
      actionInstance.eventEmitter.once('cancel', () => {
        return resolve();
      });

      actionInstance.eventEmitter.once('succeed', () => {
        return resolve();
      });

      actionInstance.eventEmitter.once('fail', (_, reason: string) => {
        this.fail(reason);
        return resolve();
      });
    });
  }
}
