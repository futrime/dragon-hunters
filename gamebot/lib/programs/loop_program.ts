import {ActionInvocation} from './action_invocation.js';
import {Program} from './program.js';

export class LoopProgram extends Program {
  constructor(public readonly program: Program, public readonly count: number) {
    super();
  }

  override[Symbol.iterator](): Iterator<ActionInvocation> {
    const program = this.program;
    const count = this.count;

    let index = 0;
    let iterator = program[Symbol.iterator]();

    return {
      next(): IteratorResult<ActionInvocation> {
        if (index < count) {
          let result = iterator.next();

          while (result.done && index < count) {
            index++;
            iterator = program[Symbol.iterator]();
            result = iterator.next();
          }

          if (index >= count) {
            return {done: true, value: null};
          }

          return result;

        } else {
          return {done: true, value: null};
        }
      }
    }
  }
}
