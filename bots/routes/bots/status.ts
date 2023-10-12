import assert from 'assert';
import consola from 'consola';
import express from 'express';

export const router = express.Router();

router.route('/').get((req, res) => {
  try {
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
});
