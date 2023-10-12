export interface Arg {
  readonly name: string;
  readonly value: unknown;
}

/**
 * Check if the given arguments contain duplicate names.
 * @param args Arguments to check.
 * @returns True if the given arguments contain duplicate names.
 */
export function isArgArrayDuplicate(args: ReadonlyArray<Arg>): boolean {
  const argNames = new Set<string>();
  for (const arg of args) {
    if (argNames.has(arg.name)) {
      return true;
    }
    argNames.add(arg.name);
  }
  return false;
}
