// import { useQuery } from "react-query";

// const CML_BASE_APIV2 = import.meta.env.VITE_CDSW_API_URL ? import.meta.env.VITE_CDSW_API_URL.replace("v1", "v2") : "";

// export const API_ENDPOINTS = {
//     getJob: `${CML_BASE_APIV2}/projects`,
// };

// async function getJobById(): Promise<any> {
//     let response;

//     try {
//         response = await fetch(API_ENDPOINTS.getExports);
//     } catch (error) {
//         return Promise.reject(error);
//     }

//     return Promise.resolve(response);
// };

// const usegetJobById = () => {
//     return useQuery({ queryKey: [`${API_ENDPOINTS.getExports}`], queryFn: getJobById })
// };

// export { usegetJobById };