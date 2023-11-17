import Ajv from "ajv";
import assert from "assert";
import consola from "consola";
import express from "express";

import {} from "../../lib/events/bot_event.js";
import { Bot } from "../../lib/bot.js";

export const router = express.Router();

router.route("/").get((req, res) => {
  try {
    const bot: Bot = req.app.locals.bot;
    const since: string = req.query.since as string;

    if (since) {
      // if exists param: since
      // check?
      const events = bot.getEvents();

      const sinceDate = new Date(since); // 解析 since 参数为日期对象

      return res.status(200).send({
        apiVersion: "0.0.0",
        data: {
          items: events
            .filter((event) => new Date(event.updatedTime) > sinceDate) // 过滤更新时间在 since 之后的事件
            .map((event) => {
              return {
                id: event.id,
                name: event.name,
                description: event.description,
                updated: new Date(event.updatedTime).toISOString(),
                args: event.args,
              };
            }),
        },
      });
    } else {
      // not have 'since'
      throw new Error(
        "params must contain 'since' or 'since' cannot be parsed as string."
      );
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
