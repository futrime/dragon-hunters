import Ajv from "ajv";
import assert from "assert";
import consola from "consola";
import express from "express";

import {} from "../../lib/events/bot_event.js";
import { Bot } from "../../lib/bot.js";

export const router = express.Router();

let updated = new Date();

router.route("/").get((req, res) => {
  try {
    const bot: Bot = req.app.locals.bot;
    const since = req.query.since;

    if (since) {
      // if exists param: since
      // check?
      const events = bot.getEvents();

      return res.status(200).send({
        apiVersion: "0.0.0",
        data: {
          items: events.map((event) => {
            return {
              id: event.id,
              name: event.name,
              description: event.description,
              updated: updated.toISOString(),
              args: event.args,
            };
          }),
        },
      });
    } else {
      // not have 'since'
      throw new Error("params must contain 'since'");
    }
  } catch (error) {
    assert(error instanceof Error);

    consola.error(`Error: ${error.message}`);
    return res.status(500).send({
      apiVersion: "0.0.0",
      error: {
        code: 500,
        message: `Internal server error occured.`,
      },
    });
  }
});
