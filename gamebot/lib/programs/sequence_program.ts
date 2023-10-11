import {ActionInvocation} from './action_invocation.js';
import {Program} from './program.js';

export class SequenceProgram extends Program {
  constructor(public readonly sequence: Program[]) {
    super();
  }

  override[Symbol.iterator](): Iterator<ActionInvocation> {
    const sequence = this.sequence;

    let index = 0;
    let iterator = sequence[index][Symbol.iterator]();

    return {
      next(): IteratorResult<ActionInvocation> {
        if (index < sequence.length) {
          let result = iterator.next();

          while (result.done && index < sequence.length) {
            index++;
            iterator = sequence[index][Symbol.iterator]();
            result = iterator.next();
          }

          if (index >= sequence.length) {
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
