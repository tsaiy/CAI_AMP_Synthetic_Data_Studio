export interface User {
    username: string;
    name: string;
    email: string;
}

export interface JobResponse {
    id: string;
    cpu: number;
    created_at: string;
    creator: User;
    engine_image_id: string;
    english_schedule: string;
    arguments: string;
    type: string;
    kernel: string;
    memory: number;
    name: string;
    parent_id: string;
    paused: boolean;
    schedule: string;
    script: string;
    timeout: string;
    timezone: string;
    updated_at: string;
    environment: string;
    nvidia_gpu: number;
    runtime_identifier: string;
    runtime_addon_identifiers: string[];
    kill_on_timeout: boolean;
}