import {ActionInvocation} from './action_invocation.js';

export abstract class Program {
  abstract[Symbol.iterator](): Iterator<ActionInvocation>;
}
