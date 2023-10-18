import {consola} from 'consola';
import EventEmitter from 'events';

import {Arg, isArgArrayDuplicate} from '../arg.js'
import {Bot} from '../bot.js';

import {ActionInstanceState} from './action_instance_state.js';

export abstract class ActionInstance {
  readonly args: Record<string, Arg>;
  readonly eventEmitter = new EventEmitter();

  private wrappedMessage: string = '';
  private wrappedState: ActionInstanceState = ActionInstanceState.READY;

  constructor(
      readonly id: string, readonly actionName: string,
      args: ReadonlyArray<Arg>, protected readonly bot: Bot) {
    if (isArgArrayDuplicate(args)) {
      throw new Error('duplicate argument');
    }

    this.args = {};
    for (const arg of args) {
      this.args[arg.name] = arg;
    }
  }

  get message(): string {
    return this.wrappedMessage;
  }

  get state(): ActionInstanceState {
    return this.wrappedState;
  }

  /**
   * Cancels the action instance.
   */
  async cancel(): Promise<void> {
    if (this.wrappedState !== ActionInstanceState.RUNNING &&
        this.wrappedState !== ActionInstanceState.PAUSED) {
      throw new Error(
          `cannot cancel an action instance in state ${this.wrappedState}`);
    }

    await this.cancelRun();

    this.wrappedState = ActionInstanceState.CANCELED;
    this.eventEmitter.emit('cancel', this);
    consola.log(`${this.actionName}#${this.id} canceled`);
  }

  /**
   * Pauses the action instance.
   */
  async pause(): Promise<void> {
    if (this.wrappedState !== ActionInstanceState.RUNNING) {
      throw new Error(
          `cannot pause an action instance in state ${this.wrappedState}`);
    }

    await this.pauseRun();

    this.wrappedState = ActionInstanceState.PAUSED;
    this.eventEmitter.emit('pause', this);
    consola.log(`${this.actionName}#${this.id} paused`);
  }

  /**
   * Resumes the action instance.
   */
  async resume(): Promise<void> {
    if (this.wrappedState !== ActionInstanceState.PAUSED) {
      throw new Error(
          `cannot resume an action instance in state ${this.wrappedState}`);
    }

    if (this.bot.isRunningAnyJob()) {
      throw new Error('cannot resume a job because another job is running');
    }

    await this.resumeRun();

    this.wrappedState = ActionInstanceState.RUNNING;
    this.eventEmitter.emit('resume', this);
    consola.log(`${this.actionName}#${this.id} resumed`);
  }

  /**
   * Starts the action instance.
   */
  async start(): Promise<void> {
    if (this.wrappedState !== ActionInstanceState.READY) {
      throw new Error(
          `cannot start an action instance in state ${this.wrappedState}`);
    }

    if (this.bot.isRunningAnyJob()) {
      throw new Error('cannot start a job because another job is running');
    }

    await this.startRun();

    this.wrappedState = ActionInstanceState.RUNNING;
    this.eventEmitter.emit('start', this);
    consola.log(`${this.actionName}#${this.id} started`);
  }

  protected abstract cancelRun(): Promise<void>;

  protected fail(reason: string): void {
    this.wrappedMessage = reason;
    this.wrappedState = ActionInstanceState.FAILED;
    this.eventEmitter.emit('fail', this, reason);
    consola.log(`${this.actionName}#${this.id} failed: ${reason}`);
  }

  protected abstract pauseRun(): Promise<void>;

  protected abstract resumeRun(): Promise<void>;

  protected abstract startRun(): Promise<void>;

  protected succeed(): void {
    this.wrappedState = ActionInstanceState.SUCCEEDED;
    this.eventEmitter.emit('succeed', this);
    consola.log(`${this.actionName}#${this.id} succeeded`);
  }
}
