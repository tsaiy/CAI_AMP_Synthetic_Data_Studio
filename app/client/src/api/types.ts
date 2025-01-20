import { QuestionSolution } from '../pages/DataGenerator/types';
import { ModelParameters } from '../types';

export type FetchModelsResp = {
    models: {
        [key: string]: string[] 
    }
}

export type FetchTopicsResp = {
    topics: string[]
}

export type FetchExamplesResp = {
    examples: QuestionSolution[]
}

export interface UseFetchApiReturn<T> {
    data: T | null;
    loading: boolean;
    error: Error | null;
}

export interface UseDeferredFetchApiReturn<T> {
    data: T | null;
    loading: boolean;
    error: Error | null;
    fetchData: () => Promise<void>;
}

export type FetchDefaultPromptResp = string;
export type FetchDefaultSchemaResp = string;

export type ModelParamDefaults = {
    min: number;
    max: number;
    default: number;
};
export interface FetchDefaultParamsResp {
    parameters: Record<ModelParameters, ModelParamDefaults>;
}
