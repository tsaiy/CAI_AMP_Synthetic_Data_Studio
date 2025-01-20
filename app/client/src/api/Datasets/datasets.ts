import { useDeleteApi, useGetApi, usePostApi } from "../hooks";
import { DatasetResponse, DeleteDatasetResponse, ExportDatasetResponse } from "./response";

const BASE_API_URL = import.meta.env.VITE_AMP_URL;

export const API_ENDPOINTS = {
  datasets: `${BASE_API_URL}/generations`,
  datasetsHistory: `${BASE_API_URL}/generations/history`,
  exportDataset: `${BASE_API_URL}/export_results`,
};

const useGetDatasetHistory = () => {
    const url = `${API_ENDPOINTS.datasetsHistory}`;
    return useGetApi<DatasetResponse[]>(url);
}

const useDeleteDataset = () => {
    const url = `${API_ENDPOINTS.datasets}`;
    return useDeleteApi<DeleteDatasetResponse>(url);
};

const usePostExportDataset = () => { 
  const url = `${API_ENDPOINTS.exportDataset}`;
  return usePostApi<ExportDatasetResponse>(url);
}

export { useGetDatasetHistory, useDeleteDataset, usePostExportDataset };