import { ExportType } from "../../types";

export interface DatasetExportRequest {
    export_type: ExportType[];
    file_path: string;
    hf_config?: HuggingFaceConfiguration;
}

export interface HuggingFaceConfiguration {
    hf_commit_message: string;
    hf_repo_name: string; // This is custom named exported data
    hf_token: string;   // This is the personal access token
    hf_username: string; // This is the namespace name in Huggingface
}