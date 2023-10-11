import Ajv from 'ajv';
import assert from 'assert';

import {ActionProgram} from './action_program.js';
import {LoopProgram} from './loop_program.js';
import {Program} from './program.js';
import {SequenceProgram} from './sequence_program.js';

export function createProgram(json: unknown): Program {
  const SCHEMA = {
    'type': 'object',
    'properties': {
      'type': {
        'type': 'string',
        'enum': ['action', 'loop', 'sequence'],
      },
    },
    'required': ['type'],
  };

  if (new Ajv().validate(SCHEMA, json) === false) {
    throw new Error('invalid JSON');
  }

  const data = json as {type: string};
  switch (data.type) {
    case 'action':
      return createActionProgram(json);

    case 'loop':
      return createLoopProgram(json);

    case 'sequence':
      return createSequenceProgram(json);

    default:
      assert.fail(`unknown program type: ${data.type}`);
  }
}

function createActionProgram(json: unknown): ActionProgram {
  const SCHEMA = {
    'type': 'object',
    'properties': {
      'action': {
        'type': 'object',
        'properties': {
          'name': {
            'type': 'string',
          },
          'args': {
            'type': 'array',
            'items': {
              'type': 'object',
              'properties': {
                'name': {
                  'type': 'string',
                },
                'value': {},
              },
              'required': ['name', 'value']
            }
          }
        },
        'required': ['name', 'args']
      },
      'type': {
        'type': 'string',
        'enum': ['action'],
      }
    },
    'required': ['type', 'action']
  };

  if (new Ajv().validate(SCHEMA, json) === false) {
    throw new Error('invalid JSON');
  }

  const data = json as {
    type: string,
    action: {
      name: string,
      args: {name: string, value: unknown}[],
    }
  };
  return new ActionProgram(data.action.name, data.action.args);
}

function createLoopProgram(json: unknown): LoopProgram {
  const SCHEMA = {
    'type': 'object',
    'properties': {
      'type': {
        'type': 'string',
        'enum': ['loop'],
      },
      'loop': {
        'type': 'object',
        'properties': {
          'count': {
            'type': 'integer',
          },
          'program': {
            'type': 'object',
          },
        },
        'required': ['count', 'program']
      }
    },
    'required': ['type', 'loop']
  };

  if (new Ajv().validate(SCHEMA, json) === false) {
    throw new Error('invalid JSON');
  }

  const data = json as {
    type: string,
    loop: {
      count: number,
      program: unknown,
    }
  };

  return new LoopProgram(createProgram(data.loop.program), data.loop.count);
}

function createSequenceProgram(json: unknown): SequenceProgram {
  const SCHEMA = {
    'type': 'object',
    'properties': {
      'type': {
        'type': 'string',
        'enum': ['sequence'],
      },
      'sequence': {
        'type': 'object',
        'properties': {
          'items': {
            'type': 'array',
            'items': {'type': 'object'},
          },
        },
        'required': ['items'],
      }
    },
    'required': ['type', 'sequence']
  };

  if (new Ajv().validate(SCHEMA, json) === false) {
    throw new Error('invalid JSON');
  }

  const data = json as {
    type: string,
    sequence: {
      items: unknown[],
    }
  };

  const items = data.sequence.items.map((item) => createProgram(item));
  return new SequenceProgram(items);
}
