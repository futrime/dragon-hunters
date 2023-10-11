import {faker} from '@faker-js/faker';
import Ajv from 'ajv';
import assert from 'assert';
import consola from 'consola';
import express, {RequestHandler} from 'express';
import path from 'path';

import {Bot} from '../lib/bot.js';

export const router = express.Router();

let updated = new Date();

router.route('/').get((req, res) => {
  try {
    const bots = req.app.locals.bots;

    return res.status(200).send({
      apiVersion: '0.0.0',
      data: {
        updated: updated.toISOString(),
        items: bots.map((bot: Bot) => {
          return {
            ip: bot.ip,
            name: bot.username,
            port: bot.port,
            updated: bot.updated.toISOString(),
          };
        }),
      },
    });

  } catch (error) {
    assert(error instanceof Error)

    consola.error(`Error: ${error.message}`);
    return res.status(500).send({
      apiVersion: '0.0.0',
      error: {
        code: 500,
        message: `Internal server error occured.`,
      },
    });
  }
});

router.route('/').post((req, res) => {
  try {
    const currentTime = new Date();

    const bots: Bot[] = req.app.locals.bots;

    const ip = req.ip;
    for (const bot of bots) {
      if (bot.ip === ip) {
        return res.status(201).send({
          apiVersion: '0.0.0',
          data: {
            name: bot.username,
          },
        });
      }
    }

    let responseJson;
    try {
      responseJson = JSON.parse(req.body);
    } catch (error) {
      assert(error instanceof Error)

      return res.status(400).send({
        apiVersion: '0.0.0',
        error: {
          code: 400,
          message: `The request is invalid: ${error.message}`,
        },
      });
    }

    // Validate response.
    const SCHEMA = {
      'type': 'object',
      'properties': {
        'apiVersion': {'type': 'string'},
        'data': {
          'type': 'object',
          'properties': {'port': {'type': 'integer'}},
          'required': ['port']
        }
      },
      'required': ['apiVersion', 'data']
    };
    const ajv = new Ajv();
    const validate = ajv.compile(SCHEMA);
    const valid = validate(responseJson);
    if (valid !== true) {
      return res.status(400).send({
        apiVersion: '0.0.0',
        error: {
          code: 400,
          message: `The request is invalid: ${ajv.errorsText(validate.errors)}`,
        },
      });
    }

    const port = responseJson.data.port;
    const username =
        bots.length === 0 ? 'Commander' : faker.person.firstName('female');

    const bot = new Bot(ip, port, username, currentTime);
    bots.push(bot);
    updated = currentTime;

    // HTTP 201 Created requires a Location header.

    return res.status(201)
        .set(
            'Location',
            `${req.protocol}://${req.get('host')}/api/bots/${bot.username}`,
            )
        .send({
          apiVersion: '0.0.0',
          data: {
            name: bot.username,
          },
        });

  } catch (error) {
    assert(error instanceof Error)

    consola.error(`Error: ${error.message}`);
    return res.status(500).send({
      apiVersion: '0.0.0',
      error: {
        code: 500,
        message: `Internal server error occured.`,
      },
    });
  }
});

router.route('/:username/*')
    .all((async (req, res) => {
           try {
             const bots: Bot[] = req.app.locals.bots;

             const bot = bots.find((bot: Bot) => {
               return bot.username === req.params.username;
             });

             if (bot === undefined) {
               res.status(404);
               res.send({
                 apiVersion: '0.0.0',
                 error: {
                   code: 404,
                   message:
                       `Bot with username ${req.params.username} not found.`,
                 },
               });
               return;
             }

             // Act as a reverse proxy.
             try {
               const requestHeaders = new Headers();
               for (const [key, value] of Object.entries(req.headers)) {
                 requestHeaders.set(key, value?.toString() ?? '');
               }

               const url = path.join(
                   `http://${bot.ip}:${bot.port}/api/bots/${bot.username}`,
                   req.params[0]);

               const response = await fetch(url, {
                 headers: requestHeaders,
                 method: req.method,
                 body: (req.method === 'GET' || req.method === 'HEAD') ?
                     undefined :
                     req.body,
               });

               res.status(response.status);
               response.headers.forEach((value, key) => {
                 res.setHeader(key, value);
               });
               res.send(await response.text());

             } catch (error) {
               assert(error instanceof Error)

               consola.error(`Error: ${error.message}`);
               res.status(502).send({
                 apiVersion: '0.0.0',
                 error: {
                   code: 502,
                   message: `Error occured while communicating with bot: ${
                       error.message}`,
                 },
               });
             }

           } catch (error) {
             assert(error instanceof Error)

             consola.error(`Error: ${error.message}`);
             return res.status(500).send({
               apiVersion: '0.0.0',
               error: {
                 code: 500,
                 message: `Internal server error occured.`,
               },
             });
           }
         }) as RequestHandler);
