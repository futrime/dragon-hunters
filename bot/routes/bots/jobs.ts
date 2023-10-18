import Ajv from 'ajv';
import assert from 'assert';
import consola from 'consola';
import express from 'express';

import {ActionInstanceState} from '../../lib/actions/action_instance_state.js';
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
      data: {action: string; args: {name: string; value: unknown}[]};
    };

    const id = bot.createJob(data.data.action, data.data.args);

    return res.status(201).send({
      apiVersion: '0.0.0',
      data: {
        id: id,
        action: data.data.action,
        args: data.data.args,
        state: bot.getJob(id)!.state,
        message: bot.getJob(id)!.message,
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
    .post(
        (async (req, res) => {
          try {
            const jobID = req.params.jobID;
            const operation = req.params.operation;

            const bot: Bot = req.app.locals.bot;
            // Find the job according to its id
            const job = bot.getJob(jobID);
            if (job === undefined) {
              return res.status(400).send({
                apiVersion: '0.0.0',
                error: {
                  code: 400,
                  message: `Job ID not found!`,
                },
              });
            }

            // Check if the operation is valid
            let errorMessage: string|null = null;
            if (operation === 'start' &&
                job.state !== ActionInstanceState.READY) {
              errorMessage = `Job ${
                  job.id} cannot be started because its state is ${job.state}.`;
            } else if (
                operation === 'pause' &&
                job.state !== ActionInstanceState.RUNNING) {
              errorMessage = `Job ${
                  job.id} cannot be paused because its state is ${job.state}.`;
            } else if (
                operation === 'resume' &&
                job.state !== ActionInstanceState.PAUSED) {
              errorMessage = `Job ${
                  job.id} cannot be resumed because its state is ${job.state}.`;
            } else if (
                operation === 'cancel' &&
                job.state === ActionInstanceState.SUCCEEDED) {
              errorMessage =
                  `Job ${job.id} cannot be canceled because its state is ${
                      job.state}.`;
            }

            if (errorMessage !== null) {
              return res.status(409).send({
                apiVersion: '0.0.0',
                error: {
                  code: 409,
                  message: errorMessage,
                },
              });
            }

            switch (operation) {
              case 'start':
                await job.start();
                break;
              case 'pause':
                await job.pause();
                break;
              case 'resume':
                await job.resume();
                break;
              case 'cancel':
                await job.cancel();
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

    const jobs = bot.getJobs();

    return res.status(200).send({
      apiVersion: '0.0.0',
      data: {
        items: jobs.map((job) => {
          return {
            id: job.id,
            action: job.actionName,
            args: Object.values(job.args),
            state: job.state,
            message: job.message,
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
