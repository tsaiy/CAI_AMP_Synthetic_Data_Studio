import get from 'lodash/get';
import isEmpty from 'lodash/isEmpty';
import isString from 'lodash/isString';
import { useQuery } from 'react-query';

const BASE_API_URL = import.meta.env.VITE_AMP_URL;

export const fetchPrompt = async (use_case: string, params: any) => {
    if (use_case !== 'custom') {
        const resp = await fetch(`${BASE_API_URL}/${use_case}/gen_prompt`, {
            method: 'GET'
        });
        const body = await resp.json();
        return isString(body) ? body : null;

    } else if (use_case === 'custom') {
        if (isEmpty(params.custom_prompt)) {
            return undefined;
        }
        const resp = await fetch(`${BASE_API_URL}/create_custom_prompt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params),
        });
        if (resp.status !== 200) {
            const error = await resp.json();
            throw new Error(error.message || error.detail);
        }
        const body = await resp.json();
        const prompt = get(body, 'generated_prompt');
        return isString(prompt) ? prompt : null;
    }
}

export const useGetPromptByUseCase = (use_case: string, { model_id, inference_type, custom_prompt, caii_endpoint }: Record<string, string>) => {
    const params = {
        model_id,
        inference_type,
        custom_prompt   
    }
    if (inference_type === 'CAII') {
        params.caii_endpoint = caii_endpoint;
    }
    const { data, isLoading, isError, error, isFetching } = useQuery(
        ['fetchPrompt', fetchPrompt],
        () => fetchPrompt(use_case, params),
        {
          keepPreviousData: false,
          refetchOnWindowFocus: false
        },
    );
    return {
      data,
      isLoading: isLoading || isFetching,
      isError,
      error    
    };
}