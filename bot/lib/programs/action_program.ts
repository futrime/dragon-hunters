import {Arg} from '../arg.js';

import {ActionInvocation} from './action_invocation.js';
import {Program} from './program.js';

export class ActionProgram extends Program {
  constructor(readonly action: string, readonly args: Arg[]) {
    super();
  }

  override[Symbol.iterator](): Iterator<ActionInvocation> {
    const action = this.action;
    const args = this.args;

    let visited = false;

    return {
      next(): IteratorResult<ActionInvocation> {
        if (visited) {
          return {done: true, value: null};

        } else {
          visited = true;
          return {done: false, value: {action: action, args: args}};
        }
      }
    }
  }
}
