import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import ProjectDetailsPage from './ProjectDetailsPage';
import { api } from '../services/api';

vi.mock('../services/api', () => ({
    api: {
        getProject: vi.fn(),
        createTask: vi.fn(),
    }
}));

// Provide router context mocking
vi.mock('react-router-dom', async (importOriginal) => {
    const actual = await importOriginal<any>();
    return {
        ...actual,
        useParams: vi.fn(),
    };
});
import { useParams } from 'react-router-dom';

describe('Task Creation within Project Details', () => {
    beforeEach(() => {
        vi.resetAllMocks();
    });

    const renderWithRouter = (ui: React.ReactElement) => {
        return render(<BrowserRouter>{ui}</BrowserRouter>);
    };

    it('renders task creation form within project details', async () => {
        vi.mocked(useParams).mockReturnValue({ projectId: 'proj-1' });
        vi.mocked(api.getProject).mockResolvedValueOnce({
            id: 'proj-1', name: 'proj 1', description: 'desc', owner_id: 'u1', created_at: 'now', updated_at: 'now', repository_path: null, repository_url: null
        });

        renderWithRouter(<ProjectDetailsPage />);

        await waitFor(() => {
            expect(screen.getByText(/Create New Coding Task/i)).toBeInTheDocument();
        });

        expect(screen.getByLabelText(/Task Requirements \*/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Submit Task/i })).toBeInTheDocument();
    });

    it('handles successful task creation seamlessly', async () => {
        vi.mocked(useParams).mockReturnValue({ projectId: 'proj-1' });
        vi.mocked(api.getProject).mockResolvedValueOnce({
            id: 'proj-1', name: 'proj 1', description: 'desc', owner_id: 'u1', created_at: 'now', updated_at: 'now', repository_path: null, repository_url: null
        });

        vi.mocked(api.createTask).mockResolvedValueOnce({
            id: 'task-100',
            project_id: 'proj-1',
            description: 'Refactor login',
            status: 'PENDING',
            owner_id: 'u1',
            created_at: '2023-01-01'
        });

        renderWithRouter(<ProjectDetailsPage />);

        await waitFor(() => {
            expect(screen.getByText(/Create New Coding Task/i)).toBeInTheDocument();
        });

        fireEvent.change(screen.getByLabelText(/Task Requirements \*/i), { target: { value: 'Refactor login' } });
        fireEvent.click(screen.getByRole('button', { name: /Submit Task/i }));

        await waitFor(() => {
            expect(api.createTask).toHaveBeenCalledWith({ project_id: 'proj-1', description: 'Refactor login' });
        });

        // Form submits and handles success block rendering
    });

    it('handles failed task creation correctly and maintains error blocks', async () => {
        vi.mocked(useParams).mockReturnValue({ projectId: 'proj-1' });
        vi.mocked(api.getProject).mockResolvedValueOnce({
            id: 'proj-1', name: 'proj 1', description: 'desc', owner_id: 'u1', created_at: 'now', updated_at: 'now', repository_path: null, repository_url: null
        });

        vi.mocked(api.createTask).mockRejectedValueOnce(new Error('Backend validation rejected'));

        renderWithRouter(<ProjectDetailsPage />);

        await waitFor(() => {
            expect(screen.getByText(/Create New Coding Task/i)).toBeInTheDocument();
        });

        fireEvent.change(screen.getByLabelText(/Task Requirements \*/i), { target: { value: 'Bad string' } });
        fireEvent.click(screen.getByRole('button', { name: /Submit Task/i }));

        await waitFor(() => {
            expect(screen.getByText(/Backend validation rejected/i)).toBeInTheDocument();
        });
    });
});
