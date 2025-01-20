import { useFetch, usePostApi } from './hooks';
import {
    FetchDefaultParamsResp,
    FetchDefaultPromptResp,
    FetchDefaultSchemaResp,
    FetchExamplesResp,
    FetchModelsResp,
    FetchTopicsResp,
    UseFetchApiReturn
} from './types';

const baseUrl = import.meta.env.VITE_AMP_URL;

export const usefetchTopics = (useCase: string): UseFetchApiReturn<FetchTopicsResp> => {
    const url = `${baseUrl}/use-cases/${useCase}/topics`;
    return useFetch(url);
}

export const useFetchExamples = (useCase: string): UseFetchApiReturn<FetchExamplesResp> => {
    const url = `${baseUrl}/${useCase}/gen_examples`;
    return useFetch(url);
}

export const useFetchModels = (): UseFetchApiReturn<FetchModelsResp> => {
    const url = `${baseUrl}/model/model_ID`;
    return useFetch(url);
}

export const useFetchDefaultPrompt = (use_case: string): UseFetchApiReturn<FetchDefaultPromptResp> => {
    const url = `${baseUrl}/${use_case}/gen_prompt`;
    return useFetch(url);
}

export const useFetchDefaultSchema = (): UseFetchApiReturn<FetchDefaultSchemaResp> => {
    const url = `${baseUrl}/sql_schema`;
    return useFetch(url);
}

export const useFetchDefaultModelParams = (): UseFetchApiReturn<FetchDefaultParamsResp> => {
    const url = `${baseUrl}/model/parameters`;
    return useFetch(url);
}

export const useTriggerDatagen = <T>() => {
    const genDatasetUrl = `${import.meta.env.VITE_AMP_URL}/synthesis/generate`;
    return usePostApi<T>(genDatasetUrl);
}
