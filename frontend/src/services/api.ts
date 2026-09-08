import { auth } from './firebase';
import { Project, ProjectCreate, Task, TaskCreate } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = 'ApiError';
    }
}

async function fetchWrapper<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    // Attach authorization token if user is signed in
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...options.headers as Record<string, string>,
    };

    if (auth.currentUser) {
        try {
            const token = await auth.currentUser.getIdToken();
            headers['Authorization'] = `Bearer ${token}`;
        } catch (error) {
            console.error("Failed to get ID token", error);
        }
    }

    const response = await fetch(url, {
        ...options,
        headers,
    });

    if (!response.ok) {
        if (response.status === 401) {
            // Unauthenticated response, clear auth state
            await auth.signOut();
            window.location.href = '/login';
        }
        throw new ApiError(response.status, `Network response was not ok: ${response.statusText}`);
    }

    return response.json();
}

export const api = {
    getHealth: () => fetchWrapper<{ status: string }>('/health'),
    getProjects: () => fetchWrapper<Project[]>('/projects'),
    getProject: (id: string) => fetchWrapper<Project>(`/projects/${id}`),
    createProject: (data: ProjectCreate) => fetchWrapper<Project>('/projects', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    getTask: (id: string) => fetchWrapper<Task>(`/tasks/${id}`),
    createTask: (data: TaskCreate) => fetchWrapper<Task>('/tasks', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
};
