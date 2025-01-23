import { useQuery } from "react-query";
import ExportResponse from "./response";

const BASE_API_URL = import.meta.env.VITE_AMP_URL;
const REFETCHINTERVAL_IN_MS = 10000;

export const API_ENDPOINTS = {
    getExports: `${BASE_API_URL}/exports/history`,
};

async function getExportJobs(): Promise<ExportResponse> {
    let response;

    try {
        response = await fetch(API_ENDPOINTS.getExports);

        if (!response.ok) {
            return Promise.reject(response.statusText);
        }
    } catch (error) {
        return Promise.reject(error);
    }

    const exportResponse: ExportResponse = await response.json();
    return exportResponse;
};


const useGetExportJobs = () => {
    return useQuery({ queryKey: [`${API_ENDPOINTS.getExports}`], refetchIntervalInBackground: true, refetchInterval: REFETCHINTERVAL_IN_MS, queryFn: getExportJobs })
};

export { useGetExportJobs };