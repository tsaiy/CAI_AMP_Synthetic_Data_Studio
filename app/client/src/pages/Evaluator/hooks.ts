import { notification } from 'antd';
import get from 'lodash/get';
import { useQuery } from 'react-query';

const BASE_API_URL = import.meta.env.VITE_AMP_URL;


const {
    VITE_WORKBENCH_URL,
    VITE_PROJECT_OWNER,
    VITE_CDSW_PROJECT
} = import.meta.env

const fetchDatasets = async (generate_file_name: string) => {
  const dataset_resp = await fetch(`${BASE_API_URL}/generations/${generate_file_name}`, {
    method: 'GET',
  });
  const dataset = await dataset_resp.json();
  const use_case = get(dataset, 'use_case');
  const prompt_resp = await fetch(`${BASE_API_URL}/${use_case}/eval_prompt`, {
    method: 'GET',
  });
  const prompt = await prompt_resp.json();
  const examples_resp = await fetch(`${BASE_API_URL}/${use_case}/eval_examples`, {
    method: 'GET',
  });
  const examples_body = await examples_resp.json();
  const examples = get(examples_body, 'examples');
  return {
    dataset,
    prompt,
    examples
  };
};

const fetchModels = async () => {
  const resp = await fetch(`${BASE_API_URL}/model/model_ID`, {
    method: 'GET',
  });
  return await resp.json();    
}

export const useModels = () => {
  const { data, isLoading, isError } = useQuery(
    ['models_data', fetchModels],
    () => fetchModels(),
      {
        keepPreviousData: true,
      },
    );
    const modelsMap = get(data, 'models');
     
    return {
      modelsMap,  
      data,
      isLoading,
      isError    
    };
}

export const useGetDataset = (generate_file_name: string) => {
    const { data, isLoading, isError, error } = useQuery(
        ["data", fetchDatasets],
        () => fetchDatasets(generate_file_name),
        {
          keepPreviousData: true,
        },
    );

    const dataset = get(data, 'dataset');
    const prompt = get(data, 'prompt');
    const examples = get(data, 'examples');
    console.log('error:', error);  

    if (error) {
      notification.error({
        message: 'Error',
        description: `An error occurred while fetching the prompt.\n ${error}`
      });
    }

    return {
      data,
      dataset,
      prompt,
      examples,
      isLoading,
      isError,
      error    
    };
}

const fetchEvaluate = async (evaluate_file_name: string) => {
    const evaluate_resp = await fetch(`${BASE_API_URL}/evaluations/${evaluate_file_name}`, {
      method: 'GET',
    });
    const evaluate = await evaluate_resp.json();
    const use_case = get(evaluate, 'use_case');
    const generate_file_name = get(evaluate, 'generate_file_name');
    const dataset_resp = await fetch(`${BASE_API_URL}/generations/${generate_file_name}`, {
        method: 'GET',
      });
    const dataset = await dataset_resp.json();
    const prompt_resp = await fetch(`${BASE_API_URL}/${use_case}/eval_prompt`, {
      method: 'GET',
    });
    const prompt = await prompt_resp.json();
    const examples_resp = await fetch(`${BASE_API_URL}/${use_case}/eval_examples`, {
      method: 'GET',
    });
    const examples_body = await examples_resp.json();
    const examples = get(examples_body, 'examples');
    return {
      evaluate,
      dataset,
      prompt,
      examples
    };
  };

export const useGetEvaluate = (evaluate_file_name: string) => {
    const { data, isLoading, isError } = useQuery(
        ["data", fetchEvaluate],
        () => fetchEvaluate(evaluate_file_name),
        {
          keepPreviousData: true,
        },
    );

    const evaluate = get(data, 'evaluate');
    const dataset = get(data, 'dataset');
    const prompt = get(data, 'prompt');
    const examples = get(data, 'examples');  

    return {
      data,
      evaluate,
      dataset,
      prompt,
      examples,
      isLoading,
      isError    
    };
}


export const getProjectJobsUrl = () => `${VITE_WORKBENCH_URL}/${VITE_PROJECT_OWNER}/${VITE_CDSW_PROJECT}/jobs`