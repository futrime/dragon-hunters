import 'dotenv/config';

import {faker} from '@faker-js/faker';
import consola from 'consola';
import cors from 'cors';
import express from 'express';
import morgan from 'morgan';
import process from 'process';

import {Bot} from './lib/bot.js';
import {router as routerApiBots} from './routes/bots.js';

main().catch((error) => {
  consola.error(`process exited with error: ${error.message}`);
  process.exit(1);
});

async function main() {
  // Read environment variables.
  const listen_port = parseInt(process.env.LISTEN_PORT ?? '8080');
  const log_level = parseInt(process.env.LOG_LEVEL ?? '3');
  const faker_seed = parseInt(process.env.FAKER_SEED ?? '114514');

  // Set up logging.
  consola.level = log_level

  // Setup Faker.
  faker.seed(faker_seed);

  // Set up shared data.
  const bots: Bot[] = [];

  // Set up express.
  setupExpress(bots, listen_port);
}

/**
 * Sets up express.
 * @param bots The bots.
 * @param listen_port The port of the gateway.
 * @returns The express app.
 */
function setupExpress(bots: Bot[], listen_port: number): express.Express {
  const app = express()
                  .use(morgan('tiny'))
                  .use(cors())
                  .use(express.raw({type: '*/*'}))
                  .use('/api/bots', routerApiBots)
                  .use((_, res) => {
                    res.status(404).send({
                      apiVersion: '0.0.0',
                      error: {
                        code: 404,
                        message: 'The requested resource was not found.',
                      }
                    });
                  });

  app.locals.bots = bots;

  app.listen(listen_port, '0.0.0.0', () => {
    consola.info(`listening on port ${listen_port}`);
  });

  return app;
}
