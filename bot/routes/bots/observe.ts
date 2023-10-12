import Ajv from 'ajv';
import assert from 'assert';
import consola from 'consola';
import express from 'express';

import {Bot} from '../../lib/bot.js';
import {createSerializedBot} from '../../lib/mineflayer_serialization.js';

export const router = express.Router();

router.route('/').post((req, res) => {
  try {
    const bot: Bot = req.app.locals.bot;

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
        'apiVersion': {
          'type': 'string',
        },
        'data': {
          'type': 'object',
        }
      },
      'required': ['apiVersion', 'data'],
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

    return res.status(200).send({
      apiVersion: '0.0.0',
      data: {
        bot: createSerializedBot(bot.mineflayerBot),
      },
    });

  } catch (error) {
    assert(error instanceof Error);

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
