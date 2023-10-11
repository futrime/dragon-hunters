import {Arg} from '../arg';

export interface ActionInstanceInfo {
  readonly args: Readonly<Record<string, Arg>>;
  readonly actionName: string;
  readonly id: string;
  readonly state: string;
}
