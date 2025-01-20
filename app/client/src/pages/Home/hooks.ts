import isEmpty from 'lodash/isEmpty';
import { useState } from 'react';
import { useQuery } from 'react-query';


const BASE_API_URL = import.meta.env.VITE_AMP_URL;

const fetchDatasets = async () => {
  const dataset_resp = await fetch(`${BASE_API_URL}/generations/history`, {
    method: 'GET',
  });
  const datasets = await dataset_resp.json();
  
  return {
    datasets
  };
};

const fetchEvaluations = async () => {
    const evaluations_resp = await fetch(`${BASE_API_URL}/evaluations/history`, {
      method: 'GET',
    });
    const evaluations = await evaluations_resp.json();
    
    return {
        evaluations
    };
};

export const useDatasets = () => {
    const [searchQuery, setSearchQuery] = useState<string | null>(null);
    const { data, isLoading, isError, refetch } = useQuery(
        ["fetchDatasets", fetchDatasets],
        () => fetchDatasets(),
        {
          keepPreviousData: false,
          refetchInterval: 15000
        },
    );
    if (searchQuery !== null && !isEmpty(searchQuery))  {
        const filteredData = data?.datasets.filter((dataset: any) => {
            return dataset.display_name.toLowerCase().includes(searchQuery.toLowerCase());
        });
        
        return {
            data: { datasets: filteredData },
            isLoading,
            isError,
            refetch,
            searchQuery,
            setSearchQuery
        };
    }
    return {
      data,
      isLoading,
      isError,
      refetch,
      searchQuery,
      setSearchQuery   
    };
}

export const useEvaluations = () => {
    const [searchQuery, setSearchQuery] = useState<string | null>(null);
    const { data, isLoading, isError, refetch } = useQuery(
        ["fetchEvaluations", fetchEvaluations],
        () => fetchEvaluations(),
        {
          keepPreviousData: false,
          refetchInterval: 15000
        },
    );
    if (searchQuery !== null && !isEmpty(searchQuery))  {
        const filteredData = data?.evaluations.filter((evaluation: any) => {
            return evaluation.display_name.toLowerCase().includes(searchQuery.toLowerCase());
        });
        
        return {
            data: { evaluations: filteredData },
            isLoading,
            isError,
            refetch,
            searchQuery,
            setSearchQuery
        };
    }
    return {
      data,
      isLoading,
      isError,
      refetch,
      searchQuery,
      setSearchQuery   
    };
}