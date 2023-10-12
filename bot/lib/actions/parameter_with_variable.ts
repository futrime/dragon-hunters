import {Parameter} from '../parameter.js';

export interface ParameterWithVariable extends Parameter {
  variable: string;
}
