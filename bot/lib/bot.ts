import consola from 'consola';
import minecraftData from 'minecraft-data';
import mineflayer from 'mineflayer';
import collectblock from 'mineflayer-collectblock';
import pathfinder from 'mineflayer-pathfinder';
import pvp from 'mineflayer-pvp';
import {nanoid} from 'nanoid';

import {Action} from './actions/action.js';
import {ActionInstance} from './actions/action_instance.js';
import {ActionInstanceState} from './actions/action_instance_state.js';
import {Arg} from './arg.js';
import {BotEvent} from './events/bot_event.js';
import {ChatEvent} from './events/chat_event.js';
import {WhisperEvent} from './events/whisper_event.js';

export class Bot {
  readonly mcdata: minecraftData.IndexedData;

  private actions: Record<string, Action> = {};
  private events: BotEvent[] = [];
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

    this.setupEvents();
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
   * Gets events from the bot.
   * @param since The time to get events from.
   * @returns The events.
   */
  getEvents(since: Date = new Date(0)): ReadonlyArray<BotEvent> {
    const events: BotEvent[] = [];
    for (const event of this.events) {
      if (event.updatedTime >= since) {
        events.push(event);
      }
    }

    return events;
  }

  /**
   * Gets information of a job from the bot.
   * @param id The id of the job.
   * @returns The job.
   */
  getJob(id: string): ActionInstance|undefined {
    if (!(id in this.jobs)) {
      return undefined;
    }

    return this.jobs[id];
  }

  /**
   * Get information of all jobs from the bot.
   * @returns All jobs.
   */
  getJobs(): ReadonlyArray<ActionInstance> {
    return Object.values(this.jobs);
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
             consola.log(`canceling all jobs...`);
             for (const job of Object.values(this.jobs)) {
               if (job.state === ActionInstanceState.RUNNING ||
                   job.state === ActionInstanceState.PAUSED) {
                 await job.cancel();
               }
             }

             consola.log(`bot ended, restarting in 5 seconds...`);
             await new Promise((resolve) => setTimeout(resolve, 5000));

             this.wrappedMineflayerBot =
                 this.createMineflayerBot(host, port, username, version);
           }));
    bot.on('error', (error) => {
      consola.error(`bot error: ${error.message}`);
    });
    bot.on('login', () => {
      consola.log(`bot logged in as ${bot.username}`);
    });

    return bot;
  }

  private onChatEvent(username: string, message: string): void {
    const event = new ChatEvent(
        nanoid(),
        [
          {
            name: 'username',
            value: username,
          },
          {
            name: 'message',
            value: message,
          }
        ],
        new Date());

    this.events.push(event);
    consola.log(`event ${event.name}#${event.id} {username: ${
        username}, message: ${message}}`);
  }

  private onWhisperEvent(username: string, message: string): void {
    const event = new WhisperEvent(
        nanoid(),
        [
          {
            name: 'username',
            value: username,
          },
          {
            name: 'message',
            value: message,
          }
        ],
        new Date());

    this.events.push(event);
    consola.log(`event ${event.name}#${event.id} {username: ${
        username}, message: ${message}}`);
  }

  private setupEvents(): void {
    this.mineflayerBot.on('chat', this.onChatEvent.bind(this));
    this.mineflayerBot.on('whisper', this.onWhisperEvent.bind(this));
  }
}
