import Ajv from 'ajv';
import assert from 'assert';
import consola from 'consola';
import express from 'express';

import {Bot} from '../../lib/bot.js';

export const router = express.Router();

router.route('/').post((req, res) => {
  try {
    const bot: Bot = req.app.locals.bot;

    let responseJson: unknown;
    try {
      responseJson = JSON.parse(req.body);
    } catch (error) {
      assert(error instanceof Error);

      return res.status(400).send({
        apiVersion: '0.0.0',
        error: {
          code: 400,
          message: `Request body is not valid JSON.`,
        },
      });
    }

    const SCHEMA = {
      type: 'object',
      properties: {
        apiVersion: {
          type: 'string',
        },
        data: {
          type: 'object',
          properties: {
            action: {
              type: 'string',
            },
            args: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  name: {
                    type: 'string',
                  },
                  value: {
                    type: [
                      'string',
                      'integer',
                      'boolean',
                      'array',
                      'object',
                      'number',
                      'null',
                    ],
                  },
                },
                required: ['name', 'value'],
              },
            },
          },
          required: ['action', 'args'],
        },
      },
      required: ['apiVersion', 'data'],
    };

    const ajv = new Ajv();
    const validate = ajv.compile(SCHEMA);
    const valid = validate(responseJson);
    if (!valid) {
      return res.status(400).send({
        apiVersion: '0.0.0',
        error: {
          code: 400,
          message: `The request is invalid:
          ${ajv.errorsText(validate.errors)}`,
        },
      });
    }

    const data = responseJson as {
      apiVersion: string;
      data: {action: string; args: {name: string; value: unknown;}[];};
    };

    const id = bot.createJob(data.data.action, data.data.args);

    return res.status(201).send({
      apiVersion: '0.0.0',
      data: {
        id: id,
        action: data.data.action,
        args: data.data.args,
        state: bot.getJobInfo(id)?.state,
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

router.route('/:jobID/:operation')
    .post((async (req, res) => {
            try {
              const jobID = req.params.jobID;
              const operation = req.params.operation;

              const bot: Bot = req.app.locals.bot;

              // Find job according to its id
              const jobsInfo = bot.getJobInfo(jobID);
              if (jobsInfo === undefined) {
                return res.status(400).send({
                  apiVersion: '0.0.0',
                  error: {
                    code: 400,
                    message: `Job ID not found!`,
                  },
                });
              }

              switch (operation) {
                case 'start':
                  await bot.startJob(jobID);
                  break;
                case 'pause':
                  await bot.pauseJob(jobID);
                  break;
                case 'resume':
                  await bot.resumeJob(jobID);
                  break;
                case 'cancel':
                  await bot.cancelJob(jobID);
                  break;
                default:
                  return res.status(400).send({
                    apiVersion: '0.0.0',
                    error: {
                      code: 400,
                      message: `Invalid job operation.`,
                    },
                  });
              }

              return res.status(200).send({
                apiVersion: '0.0.0',
                data: {},
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
          }) as express.RequestHandler);

router.route('/').get((req, res) => {
  try {
    const bot: Bot = req.app.locals.bot;

    const jobsInfo = bot.getJobsInfo();

    return res.status(200).send({
      apiVersion: '0.0.0',
      data: {
        items: jobsInfo.map((jobInfo) => {
          return {
            id: jobInfo.id,
            action: jobInfo.actionName,
            args: Object.values(jobInfo.args),
            state: jobInfo.state,
          };
        }),
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
