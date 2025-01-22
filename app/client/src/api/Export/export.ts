import { useQuery } from "react-query";
import ExportResponse from "./response";

const BASE_API_URL = import.meta.env.VITE_AMP_URL;

export const API_ENDPOINTS = {
    getExports: `${BASE_API_URL}/exports`,
};

async function getExportJobs(): Promise<ExportResponse> {
    let response;

    try {
        response = await fetch(API_ENDPOINTS.getExports);
    } catch (error) {
        return Promise.reject(error);
    }

    return Promise.resolve(response);
};


const useGetExportJobs = () => {
    return useQuery({ queryKey: [`${API_ENDPOINTS.getExports}`], queryFn: getExportJobs })
};

export { useGetExportJobs };