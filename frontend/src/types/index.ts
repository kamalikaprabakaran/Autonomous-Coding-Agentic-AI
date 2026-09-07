export interface Project {
    id: string;
    name: string;
    description: string;
    repository_path: string | null;
    repository_url: string | null;
    owner_id: string | null;
    created_at: string;
    updated_at: string;
}

export interface Task {
    id: string;
    project_id: string;
    description: string;
    status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
    owner_id: string | null;
    created_at: string;
}

export interface AgentRun {
    id: string;
    task_id: string;
    status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
    iteration_count: number;
    owner_id: string | null;
    started_at: string;
    completed_at: string | null;
}
