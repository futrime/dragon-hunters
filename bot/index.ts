import 'dotenv/config';

import Ajv from 'ajv';
import consola from 'consola';
import cors from 'cors';
import express from 'express';
import morgan from 'morgan';
import fetch from 'node-fetch';
import process from 'process';

import {ExploreUntilAction} from './lib/actions/explore_until_action.js';
import {GoToAction} from './lib/actions/go_to_action.js';
import {Bot} from './lib/bot.js';
import {router as routerBotsActions} from './routes/bots/actions.js';
import {router as routerBotsJobs} from './routes/bots/jobs.js';
import {router as routerBotsObserve} from './routes/bots/observe.js';
import {router as routerBotsStatus} from './routes/bots/status.js';

main().catch((error) => {
  consola.error(`process exited with error: ${error.message}`);
  process.exit(1);
});

async function main() {
  // Read environment variables.
  let bot_username = process.env.BOT_USERNAME ?? 'Unnamed';
  const listen_port = parseInt(process.env.LISTEN_PORT ?? '8080');
  const log_level = parseInt(process.env.LOG_LEVEL ?? '3');
  const mcserver_host = process.env.MCSERVER_HOST ?? '127.0.0.1';
  const mcserver_port = parseInt(process.env.MCSERVER_PORT ?? '25565');
  const mcserver_version = process.env.MCSERVER_VERSION ?? '1.20.1';
  const registry_address =
      process.env.REGISTRY_ADDRESS ?? undefined;

  // Set up logging.
  consola.level = log_level;

  if (registry_address !== undefined) {
    // Register the bot on the registry.
    consola.log('registering bot...');
    bot_username =
        (await registerBot(listen_port, registry_address).catch((error) => {
          throw new Error(`failed to register bot: ${error.message}`);
        })).username;
    consola.log(`registered bot as ${bot_username}`);
  }

  // Create the bot.
  const bot = new Bot(mcserver_host, mcserver_port, bot_username, mcserver_version);

  // Set up predefined actions.
  setupPredefinedActions(bot);

  // Set up express.
  await setupExpress(bot, listen_port).catch((error) => {
    throw new Error(`failed to set up express: ${error.message}`);
  });
}

async function registerBot(listen_port: number, registry_address: string):
    Promise<{username: string}> {
  const response = await fetch(`${registry_address}/api/bots`, {
                     method: 'POST',
                     headers: {
                       'Content-Type': 'application/json',
                     },
                     body: JSON.stringify({
                       apiVersion: '0.0.0',
                       data: {
                         port: listen_port,
                       },
                     }),
                   }).catch((error) => {
    throw new Error(
        `failed to fetch ${registry_address}/api/bots: ${error.message}`);
  });

  if (response.status !== 201) {
    throw new Error(`failed to fetch ${registry_address}/api/bots:  ${
        response.status} ${response.statusText}`);
  }

  const responseJson = await response.json().catch((error) => {
    throw new Error(`failed to parse response: ${error.message}`);
  });

  // Validate response.
  const SCHEMA = {
    type: 'object',
    properties: {
      apiVersion: {type: 'string'},
      data: {
        type: 'object',
        properties: {name: {type: 'string'}},
        required: ['name'],
      },
    },
    required: ['apiVersion', 'data'],
  };
  const ajv = new Ajv();
  const validate = ajv.compile(SCHEMA);
  const valid = validate(responseJson);
  if (valid !== true) {
    throw new Error(`got invalid response fetching ${
        registry_address}/api/bots: ${ajv.errorsText(validate.errors)}`);
  }

  const parsedResponse = responseJson as {
    apiVersion: string;
    data: {name: string;};
  };

  return {
    username: parsedResponse.data.name,
  };
}

async function setupExpress(
    bot: Bot, listen_port: number): Promise<express.Express> {
  const app = express()
                  .use(morgan('tiny'))
                  .use(cors())
                  .use(express.raw({type: '*/*'}))
                  .use(`/api/observe`, routerBotsObserve)
                  .use(`/api/status`, routerBotsStatus)
                  .use(`/api/actions`, routerBotsActions)
                  .use(`/api/jobs`, routerBotsJobs)
                  .use((_, res) => {
                    return res.status(404).send({
                      apiVersion: '0.0.0',
                      error: {
                        code: 404,
                        message: 'The requested resource was not found.',
                      },
                    });
                  });

  app.locals.bot = bot;

  app.listen(listen_port, '0.0.0.0', () => {
    consola.info(`listening on port ${listen_port}`);
  });

  return app;
}

function setupPredefinedActions(bot: Bot) {
  bot.addAction(new GoToAction());
  bot.addAction(new ExploreUntilAction);
}
