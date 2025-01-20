import { useDeleteApi, useGetApi } from "../hooks";
import { DeleteEvaluationResponse, EvaluationResponse } from "./response";

const BASE_API_URL = import.meta.env.VITE_AMP_URL;

export const API_ENDPOINTS = {
    evaluations: `${BASE_API_URL}/evaluations`,
    evaluationsHistory: `${BASE_API_URL}/evaluations/history`,
  };

const useGetEvaluationsHistory = () => {
    const url = `${API_ENDPOINTS.evaluationsHistory}`;
    return useGetApi<EvaluationResponse[]>(url);
}

const useDeleteEvaluation = () => {
    const url = `${API_ENDPOINTS.evaluations}`;
    return useDeleteApi<DeleteEvaluationResponse>(url);
};

export { useGetEvaluationsHistory, useDeleteEvaluation };