import {Arg} from './arg';

export interface Parameter {
  readonly name: string;
  readonly description: string;
  readonly type: string;
}

/**
 * Check if the given parameters contain duplicate names.
 * @param parameters Parameters to check.
 * @returns True if the given parameters contain duplicate names.
 */
export function isParameterArrayDuplicate(parameters: ReadonlyArray<Parameter>):
    boolean {
  const parameterNames = new Set<string>();
  for (const parameter of parameters) {
    if (parameterNames.has(parameter.name)) {
      return true;
    }
    parameterNames.add(parameter.name);
  }
  return false;
}

export function doArgArrayMatchParameterArray(
    args: ReadonlyArray<Arg>, parameters: ReadonlyArray<Parameter>): boolean {
  // The number of arguments must match the number of parameters.
  if (args.length !== parameters.length) {
    return false;
  }

  // Every parameter must match an argument with the proper type.
  for (const parameter of parameters) {
    let found = false;
    for (const arg of args) {
      if (parameter.name === arg.name) {
        found = true;

        if (parameter.type !== typeof arg.value) {
          return false;
        }
      }
    }

    if (!found) {
      return false;
    }
  }

  return true;
}
