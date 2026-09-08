import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import ProjectsPage from './ProjectsPage';
import { api } from '../services/api';

vi.mock('../services/api', () => ({
    api: {
        getProjects: vi.fn(),
        createProject: vi.fn(),
    }
}));

describe('Projects Dashboard UI Tests', () => {
    beforeEach(() => {
        vi.resetAllMocks();
    });

    const renderWithRouter = (ui: React.ReactElement) => {
        return render(<BrowserRouter>{ui}</BrowserRouter>);
    };

    it('renders loading state initially', async () => {
        // Return a promise that never resolves fully immediately to keep it loading
        vi.mocked(api.getProjects).mockImplementation(() => new Promise(() => { }));
        renderWithRouter(<ProjectsPage />);
        expect(screen.getByText(/Loading your dashboard\.\.\./i)).toBeInTheDocument();
    });

    it('renders empty project state when no projects exist', async () => {
        vi.mocked(api.getProjects).mockResolvedValueOnce([]);
        renderWithRouter(<ProjectsPage />);

        await waitFor(() => {
            expect(screen.getByText(/No projects yet/i)).toBeInTheDocument();
        });
        expect(screen.getByText(/Total Projects: 0/i)).toBeInTheDocument();
    });

    it('renders project list populated with API data', async () => {
        const fakeProjects = [
            { id: '1', name: 'Test Proj 1', description: 'desc 1', repository_path: '/repo', repository_url: null, owner_id: 'user1', created_at: '2023-01-01T00:00:00Z', updated_at: '2023-01-01T00:00:00Z' }
        ];
        vi.mocked(api.getProjects).mockResolvedValueOnce(fakeProjects);

        renderWithRouter(<ProjectsPage />);

        await waitFor(() => {
            expect(screen.getByText(/Test Proj 1/i)).toBeInTheDocument();
        });
        expect(screen.getByText(/Total Projects: 1/i)).toBeInTheDocument();
    });

    it('displays error state correctly', async () => {
        vi.mocked(api.getProjects).mockRejectedValueOnce(new Error('Network disconnected'));

        renderWithRouter(<ProjectsPage />);

        await waitFor(() => {
            expect(screen.getByText(/Network disconnected/i)).toBeInTheDocument();
        });
    });

    it('allows opening create project modal and creating project', async () => {
        vi.mocked(api.getProjects).mockResolvedValueOnce([]);
        renderWithRouter(<ProjectsPage />);

        await waitFor(() => {
            expect(screen.getByText(/No projects yet/i)).toBeInTheDocument();
        });

        // Click create 
        fireEvent.click(screen.getAllByText(/Create Project/i)[0]);
        expect(screen.getByLabelText(/Project Name \*/i)).toBeInTheDocument();

        // Type
        fireEvent.change(screen.getByLabelText(/Project Name \*/i), { target: { value: 'New Agentic Tool' } });

        const newProj = { id: '2', name: 'New Agentic Tool', description: '', repository_path: null, repository_url: null, owner_id: 'user1', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' };
        vi.mocked(api.createProject).mockResolvedValueOnce(newProj);

        // Submit
        fireEvent.click(screen.getAllByText(/Create Project/i).find(el => el.tagName === 'BUTTON' && el.getAttribute('type') === 'submit')!);

        await waitFor(() => {
            expect(api.createProject).toHaveBeenCalledWith({
                name: 'New Agentic Tool',
                description: undefined,
                repository_path: null,
                repository_url: null
            });
            // The modal should close and the new project should be visible
            expect(screen.getByText(/New Agentic Tool/i)).toBeInTheDocument();
            expect(screen.getByText(/Total Projects: 1/i)).toBeInTheDocument();
        });
    });
});
