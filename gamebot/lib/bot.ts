import consola from 'consola';
import minecraftData from 'minecraft-data';
import mineflayer from 'mineflayer';
import collectblock from 'mineflayer-collectblock';
import pathfinder from 'mineflayer-pathfinder';
import pvp from 'mineflayer-pvp';
import {nanoid} from 'nanoid';

import {Action} from './actions/action.js';
import {ActionInstance} from './actions/action_instance.js';
import {ActionInstanceInfo} from './actions/action_instance_info.js';
import {ActionInstanceState} from './actions/action_instance_state.js';
import {Arg} from './arg.js';

export class Bot {
  readonly mcdata: minecraftData.IndexedData;

  private actions: Record<string, Action> = {};
  private jobs: Record<string, ActionInstance> = {};
  private wrappedMineflayerBot: mineflayer.Bot;

  /**
   * @param host The server host.
   * @param port The server port.
   * @param username The username.
   * @param version The Minecraft version.
   */
  constructor(
      readonly host: string, readonly port: number, readonly username: string,
      readonly version: string) {
    this.mcdata = minecraftData(version);
    this.wrappedMineflayerBot =
        this.createMineflayerBot(host, port, username, version);
  }

  get mineflayerBot(): mineflayer.Bot {
    return this.wrappedMineflayerBot;
  }

  get name(): string {
    return this.username;
  }

  /**
   * Adds an action in the bot.
   * @param action The action to add or update.
   */
  addAction(action: Action): void {
    if (action.name in this.actions) {
      throw new Error(`action ${action.name} already exists`);
    }

    this.actions[action.name] = action;
  }

  /**
   * Cancels a job.
   * @param id The id of the job.
   */
  async cancelJob(id: string): Promise<void> {
    if (!(id in this.jobs)) {
      throw new Error(`job ${id} does not exist`);
    }

    if (this.jobs[id].state !== ActionInstanceState.RUNNING &&
        this.jobs[id].state !== ActionInstanceState.PAUSED) {
      throw new Error(`job ${id} is not running`);
    }

    await this.jobs[id].cancel();
  }

  /**
   * Creates a job.
   * @param action The action to create a job from.
   * @param args The arguments to pass to the action.
   * @returns The id of the job.
   */
  createJob(actionName: string, args: ReadonlyArray<Arg>): string {
    const id = nanoid();
    if (id in this.jobs) {
      throw new Error(`identical job id ${id} already exists`);
    }

    if (!(actionName in this.actions)) {
      throw new Error(`action ${actionName} does not exist`);
    }
    const action = this.actions[actionName];

    this.jobs[id] = action.instantiate(id, args, this);

    return id;
  }

  /**
   * Gets an action from the bot.
   * @param name The name of the action.
   * @returns The action.
   */
  getAction(name: string): Action|undefined {
    if (!(name in this.actions)) {
      return undefined;
    }

    return this.actions[name];
  }

  /**
   * Gets all actions from the bot.
   * @returns All actions.
   */
  getActions(): ReadonlyArray<Action> {
    return Object.values(this.actions);
  }

  /**
   * Gets information of a job from the bot.
   * @param id The id of the job.
   * @returns The job.
   */
  getJobInfo(id: string): ActionInstanceInfo|undefined {
    if (!(id in this.jobs)) {
      return undefined;
    }

    return this.jobs[id].info;
  }

  /**
   * Get information of all jobs from the bot.
   * @returns All jobs.
   */
  getJobsInfo(): ReadonlyArray<ActionInstanceInfo> {
    return Object.values(this.jobs).map((job) => job.info);
  }

  /**
   * Checks if any job is running.
   * @returns True if any job is running.
   */
  isRunningAnyJob(): boolean {
    for (const job of Object.values(this.jobs)) {
      if (job.state === ActionInstanceState.RUNNING) {
        return true;
      }
    }

    return false;
  }

  /**
   * Pauses a job.
   * @param id The id of the job.
   */
  async pauseJob(id: string): Promise<void> {
    if (!(id in this.jobs)) {
      throw new Error(`job ${id} does not exist`);
    }

    if (this.jobs[id].state !== ActionInstanceState.RUNNING) {
      throw new Error(`job ${id} is not running`);
    }

    await this.jobs[id].pause();
  }

  /**
   * Resumes a job.
   * @param id The id of the job.
   */
  async resumeJob(id: string): Promise<void> {
    if (!(id in this.jobs)) {
      throw new Error(`job ${id} does not exist`);
    }

    if (this.jobs[id].state !== ActionInstanceState.PAUSED) {
      throw new Error(`job ${id} is not paused`);
    }

    for (const job of Object.values(this.jobs)) {
      if (job.state === ActionInstanceState.RUNNING) {
        throw new Error(`job ${id} cannot be started because job ${
            job.id} is already running`);
      }
    }

    await this.jobs[id].resume();
  }

  /**
   * Starts a job.
   * @param id The id of the action.
   */
  async startJob(id: string): Promise<void> {
    if (!(id in this.jobs)) {
      throw new Error(`job ${id} does not exist`);
    }

    if (this.jobs[id].state !== ActionInstanceState.READY) {
      throw new Error(`job ${id} is not ready`);
    }

    for (const job of Object.values(this.jobs)) {
      if (job.state === ActionInstanceState.RUNNING) {
        throw new Error(`job ${id} cannot be started because job ${
            job.id} is already running`);
      }
    }

    await this.jobs[id].start();
  }

  private createMineflayerBot(
      host: string, port: number, username: string,
      version: string): mineflayer.Bot {
    const bot = mineflayer.createBot({
      auth: 'offline',
      host: host,
      port: port,
      username: username,
      version: version,
    });

    bot.loadPlugin(collectblock.plugin);
    bot.loadPlugin(pathfinder.pathfinder);
    bot.loadPlugin(pvp.plugin);

    bot.on('end', (async () => {
             consola.log(`bot ended, restarting in 5 seconds...`);
             await new Promise((resolve) => setTimeout(resolve, 5000));

             this.wrappedMineflayerBot =
                 this.createMineflayerBot(host, port, username, version);
           }));
    bot.on('error', (error) => {
      consola.error(`bot error: ${error.message}`);
    });
    bot.on('login', () => {
      consola.log('bot logged in');
    });

    return bot;
  }
}
