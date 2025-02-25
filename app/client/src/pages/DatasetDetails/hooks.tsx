import get from 'lodash/get';
import { notification } from 'antd';
import { useQuery } from '@tanstack/react-query';


const BASE_API_URL = import.meta.env.VITE_AMP_URL;


const {
    VITE_WORKBENCH_URL,
    VITE_PROJECT_OWNER,
    VITE_CDSW_PROJECT
} = import.meta.env



const fetchDatasetDetails = async (generate_file_name: string) => {
  const dataset_details__resp = await fetch(`${BASE_API_URL}/dataset_details/${generate_file_name}`, {
    method: 'GET',
  });
  const datasetDetails = await dataset_details__resp.json();
  const dataset__resp = await fetch(`${BASE_API_URL}/generations/${generate_file_name}`, {
    method: 'GET',
  });
  const dataset = await dataset__resp.json();
  
  return {
    dataset,
    datasetDetails
  };
};




export const useGetDatasetDetails = (generate_file_name: string) => {
    const { data, isLoading, isError, error } = useQuery(
        {
          queryKey: ['data', fetchDatasetDetails],
          queryFn: () => fetchDatasetDetails(generate_file_name),
          placeholderData: (previousData) => previousData
        }
    );

    const dataset = get(data, 'dataset');
    console.log('data:', data);  
    console.log('error:', error);  

    if (error) {
      notification.error({
        message: 'Error',
        description: `An error occurred while fetching the dataset details:\n ${error}`
      });
    }

    return {
      data,
      dataset,
      isLoading,
      isError,
      error    
    };
}