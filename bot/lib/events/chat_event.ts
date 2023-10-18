import {Arg} from '../arg.js';

import {BotEvent} from './bot_event.js';

const NAME = 'chat';

const DESCRIPTION = 'A player chats publicly.';

const PARAMETERS = [
  {
    name: 'username',
    description: 'Who said the message.',
    type: 'string',
  },
  {
    name: 'message',
    description: 'The message that was said.',
    type: 'string',
  }
];

export class ChatEvent extends BotEvent {
  constructor(id: string, args: ReadonlyArray<Arg>, updated: Date) {
    super(id, NAME, DESCRIPTION, args, PARAMETERS, updated);
  }
}
