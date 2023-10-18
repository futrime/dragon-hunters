import {Arg} from '../arg.js';

import {BotEvent} from './bot_event.js';

const NAME = 'whisper';

const DESCRIPTION = 'A player chats to you privately.';

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

export class WhisperEvent extends BotEvent {
  constructor(id: string, args: ReadonlyArray<Arg>, updated: Date) {
    super(id, NAME, DESCRIPTION, args, PARAMETERS, updated);
  }
}
