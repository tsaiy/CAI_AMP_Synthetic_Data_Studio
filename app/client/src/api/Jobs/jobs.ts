import { useQuery } from "@tanstack/react-query";
import { JobResponse } from "./response";

const CML_API_URL = import.meta.env.VITE_CDSW_API_URL.replace("v1","v2");
const PROJECT_NAME = import.meta.env.VITE_CDSW_PROJECT;
const PROJECT_OWNER = import.meta.env.VITE_PROJECT_OWNER;
const API_V2_KEY = import.meta.env.VITE_CDSW_APIV2_KEY;
const REFETCHINTERVAL_IN_MS = 10000;

export const API_ENDPOINTS = {
    getJobs: `${CML_API_URL}/projects`,
};

async function getJobs(): Promise<JobResponse[]> {
    let response;
    const apiUrl = `${API_ENDPOINTS.getJobs}/${PROJECT_OWNER}/${PROJECT_NAME}/jobs`;

    try {
        response = await fetch(apiUrl, { headers: { 'Authorization': `Bearer ${API_V2_KEY}` } });

        if (!response.ok) {
            return Promise.reject(response.statusText);
        }
    } catch (error) {
        return Promise.reject(error);
    }

    const exportResponse: JobResponse[] = await response.json();
    return exportResponse;
};


const useGetJobs = () => {
    return useQuery({ queryKey: [`${API_ENDPOINTS.getJobs}`], refetchIntervalInBackground: true, refetchInterval: REFETCHINTERVAL_IN_MS, queryFn: getJobs })
};

export { useGetJobs };