
export interface ExportResponse {
    jobs: Job[];
}export interface Job {
    display_export_name: string;
    display_name: string | null;
    hf_export_path: string;
    id: number;
    job_id: string;
    job_name: string;
    job_status: JobStatus;
    local_export_path: string;
    timestamp: string;
}

export type JobStatus = "success" |  "failure" | "in progress";