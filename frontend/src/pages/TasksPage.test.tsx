import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import TasksPage from './TasksPage';
import { api, ApiError } from '../services/api';

vi.mock('../services/api', () => ({
    api: {
        getTask: vi.fn(),
    },
    ApiError: class ApiError extends Error {
        status: number;
        constructor(status: number, message: string) {
            super(message);
            this.name = 'ApiError';
            this.status = status;
        }
    },
}));

vi.mock('react-router-dom', async (importOriginal) => {
    const actual = await importOriginal<any>();
    return {
        ...actual,
        useParams: vi.fn(),
    };
});
import { useParams } from 'react-router-dom';

describe('TasksPage Tests', () => {
    beforeEach(() => {
        vi.resetAllMocks();
    });

    const renderWithRouter = (ui: React.ReactElement) => {
        return render(<BrowserRouter>{ui}</BrowserRouter>);
    };

    it('renders search form when no taskId is provided', () => {
        vi.mocked(useParams).mockReturnValue({});
        renderWithRouter(<TasksPage />);
        expect(screen.getByText(/Find Task/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/Enter Task ID/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Search/i })).toBeInTheDocument();
    });

    it('shows loading state while fetching task', async () => {
        vi.mocked(useParams).mockReturnValue({ taskId: 'task-1' });
        // Never resolves — keeps loading
        vi.mocked(api.getTask).mockReturnValue(new Promise(() => { }));

        renderWithRouter(<TasksPage />);
        expect(screen.getByText(/Loading Task details/i)).toBeInTheDocument();
    });

    it('renders task details on successful API response', async () => {
        vi.mocked(useParams).mockReturnValue({ taskId: 'task-abc' });
        vi.mocked(api.getTask).mockResolvedValueOnce({
            id: 'task-abc',
            project_id: 'proj-1',
            description: 'Build authentication module',
            status: 'PENDING',
            owner_id: 'user-1',
            created_at: '2024-01-15T10:00:00Z',
        });

        renderWithRouter(<TasksPage />);

        await waitFor(() => {
            expect(screen.getByText('Task Details')).toBeInTheDocument();
        });

        expect(screen.getByText('task-abc')).toBeInTheDocument();
        expect(screen.getByText('Build authentication module')).toBeInTheDocument();
        expect(screen.getByText('PENDING')).toBeInTheDocument();
    });

    it('shows 404 error state when task is not found', async () => {
        vi.mocked(useParams).mockReturnValue({ taskId: 'bad-id' });
        const err = new ApiError(404, 'Task not found');
        vi.mocked(api.getTask).mockRejectedValueOnce(err);

        renderWithRouter(<TasksPage />);

        await waitFor(() => {
            expect(screen.getByText(/Task not found/i)).toBeInTheDocument();
        });
    });

    it('shows generic error state on server error', async () => {
        vi.mocked(useParams).mockReturnValue({ taskId: 'task-x' });
        vi.mocked(api.getTask).mockRejectedValueOnce(new Error('Internal server error'));

        renderWithRouter(<TasksPage />);

        await waitFor(() => {
            expect(screen.getByText(/Internal server error/i)).toBeInTheDocument();
        });
    });

    it('shows COMPLETED status badge with correct styling', async () => {
        vi.mocked(useParams).mockReturnValue({ taskId: 'task-done' });
        vi.mocked(api.getTask).mockResolvedValueOnce({
            id: 'task-done',
            project_id: 'proj-2',
            description: 'Task completed',
            status: 'COMPLETED',
            owner_id: 'u1',
            created_at: '2024-01-16T12:00:00Z',
        });

        renderWithRouter(<TasksPage />);

        await waitFor(() => {
            expect(screen.getByText('COMPLETED')).toBeInTheDocument();
        });
    });

    it('shows FAILED status badge', async () => {
        vi.mocked(useParams).mockReturnValue({ taskId: 'task-fail' });
        vi.mocked(api.getTask).mockResolvedValueOnce({
            id: 'task-fail',
            project_id: 'proj-3',
            description: 'Failed task',
            status: 'FAILED',
            owner_id: 'u1',
            created_at: '2024-01-17T08:00:00Z',
        });

        renderWithRouter(<TasksPage />);

        await waitFor(() => {
            expect(screen.getByText('FAILED')).toBeInTheDocument();
        });
    });

    it('shows back-link to parent project after loading task', async () => {
        vi.mocked(useParams).mockReturnValue({ taskId: 'task-xyz' });
        vi.mocked(api.getTask).mockResolvedValueOnce({
            id: 'task-xyz',
            project_id: 'proj-parent',
            description: 'My task',
            status: 'RUNNING',
            owner_id: 'u1',
            created_at: '2024-01-18T09:00:00Z',
        });

        renderWithRouter(<TasksPage />);

        await waitFor(() => {
            expect(screen.getByText(/Back to Parent Project/i)).toBeInTheDocument();
        });
    });

    it('shows agent execution section on task details page', async () => {
        vi.mocked(useParams).mockReturnValue({ taskId: 'task-agent' });
        vi.mocked(api.getTask).mockResolvedValueOnce({
            id: 'task-agent',
            project_id: 'proj-4',
            description: 'Agent task',
            status: 'PENDING',
            owner_id: 'u1',
            created_at: '2024-01-19T11:00:00Z',
        });

        renderWithRouter(<TasksPage />);

        await waitFor(() => {
            expect(screen.getByText(/Agent Execution/i)).toBeInTheDocument();
        });

        expect(screen.getByText(/No Agent Start Endpoint Available/i)).toBeInTheDocument();
    });
});
