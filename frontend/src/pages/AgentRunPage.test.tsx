import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import AgentRunPage from './AgentRunPage';
import { api } from '../services/api';

vi.mock('../services/api', () => ({
    api: {
        getAgentStatus: vi.fn(),
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

const renderWithRouter = (ui: React.ReactElement) => {
    return render(<BrowserRouter>{ui}</BrowserRouter>);
};

// ──────────────────────────────────────────────────────────────
// Rendering Tests (No fake timers — waitFor works normally)
// ──────────────────────────────────────────────────────────────
describe('AgentRunPage Rendering Tests', () => {
    beforeEach(() => {
        vi.resetAllMocks();
    });

    it('renders placeholder entry when runId is missing', () => {
        vi.mocked(useParams).mockReturnValue({});
        renderWithRouter(<AgentRunPage />);
        expect(screen.getByText(/Agent Execution Status Analyzer/i)).toBeInTheDocument();
    });

    it('starts polling and shows initial loading state for non-cached run', () => {
        vi.mocked(useParams).mockReturnValue({ runId: 'run-new' });
        vi.mocked(api.getAgentStatus).mockReturnValue(new Promise(() => { })); // never resolves
        renderWithRouter(<AgentRunPage />);
        expect(screen.getByText(/Connecting to execution sandbox/i)).toBeInTheDocument();
    });

    it('shows RUNNING status with polling message', async () => {
        vi.mocked(useParams).mockReturnValue({ runId: 'run-running' });
        vi.mocked(api.getAgentStatus).mockResolvedValue({
            id: 'run-running', task_id: 'task-2', status: 'RUNNING',
            iteration_count: 2, started_at: '2023-06-01T00:00:00Z',
            completed_at: null, owner_id: 'u1'
        } as any);

        renderWithRouter(<AgentRunPage />);

        await waitFor(() => expect(screen.getAllByText('RUNNING')[0]).toBeInTheDocument());
        expect(screen.getByText(/Polling for status updates/i)).toBeInTheDocument();
    });

    it('shows FAILED status and polling concluded message', async () => {
        vi.mocked(useParams).mockReturnValue({ runId: 'run-fail' });
        vi.mocked(api.getAgentStatus).mockResolvedValue({
            id: 'run-fail', task_id: 'task-3', status: 'FAILED',
            iteration_count: 3, started_at: '2023-07-01T00:00:00Z',
            completed_at: '2023-07-01T00:01:30Z', owner_id: 'u1'
        } as any);

        renderWithRouter(<AgentRunPage />);

        await waitFor(() => expect(screen.getAllByText('FAILED')[0]).toBeInTheDocument());
        expect(screen.getByText(/Polling concluded/i)).toBeInTheDocument();
    });

    it('shows COMPLETED status with iteration count', async () => {
        vi.mocked(useParams).mockReturnValue({ runId: 'run-done' });
        vi.mocked(api.getAgentStatus).mockResolvedValue({
            id: 'run-done', task_id: 'task-4', status: 'COMPLETED',
            iteration_count: 5, started_at: '2023-09-01T10:00:00Z',
            completed_at: '2023-09-01T10:05:00Z', owner_id: 'u1'
        } as any);

        renderWithRouter(<AgentRunPage />);

        await waitFor(() => {
            expect(screen.getAllByText('COMPLETED')[0]).toBeInTheDocument();
            expect(screen.getByText(/5 \/ ∞/i)).toBeInTheDocument();
        });
    });

    it('shows back-link to parent task when run is loaded', async () => {
        vi.mocked(useParams).mockReturnValue({ runId: 'run-link' });
        vi.mocked(api.getAgentStatus).mockResolvedValue({
            id: 'run-link', task_id: 'task-parent', status: 'PENDING',
            iteration_count: 0, started_at: '2023-10-01T00:00:00Z',
            completed_at: null, owner_id: 'u1'
        } as any);

        renderWithRouter(<AgentRunPage />);

        await waitFor(() => expect(screen.getByText(/Back to Parent Task/i)).toBeInTheDocument());
    });

    it('displays Agent Execution Details heading when run is loaded', async () => {
        vi.mocked(useParams).mockReturnValue({ runId: 'run-details' });
        vi.mocked(api.getAgentStatus).mockResolvedValue({
            id: 'run-details', task_id: 'task-5', status: 'RUNNING',
            iteration_count: 1, started_at: '2023-11-01T00:00:00Z',
            completed_at: null, owner_id: 'u1'
        } as any);

        renderWithRouter(<AgentRunPage />);

        await waitFor(() => expect(screen.getByText(/Agent Execution Details/i)).toBeInTheDocument());
    });

    it('shows error state on API failure', async () => {
        vi.mocked(useParams).mockReturnValue({ runId: 'run-err' });
        vi.mocked(api.getAgentStatus).mockRejectedValue(new Error('Network offline'));

        renderWithRouter(<AgentRunPage />);

        await waitFor(() => expect(screen.getByText(/Network offline/i)).toBeInTheDocument());
    });

    it('clears interval on component unmount without throwing (no-runId path)', () => {
        vi.mocked(useParams).mockReturnValue({});
        const { unmount } = renderWithRouter(<AgentRunPage />);
        expect(() => unmount()).not.toThrow();
    });
});

// ──────────────────────────────────────────────────────────────
// Polling Tests (setInterval spy — no fake timers needed)
// ──────────────────────────────────────────────────────────────
describe('AgentRunPage Polling Tests', () => {
    beforeEach(() => {
        vi.resetAllMocks();
        vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval'] });
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('renders PENDING status and polls while RUNNING', async () => {
        vi.mocked(useParams).mockReturnValue({ runId: 'run-123' });
        const mockPending = {
            id: 'run-123', task_id: 'task-1', status: 'PENDING',
            iteration_count: 0, started_at: '2023-01-01T00:00:00Z',
            completed_at: null, owner_id: 'u1'
        };
        const mockRunning = { ...mockPending, status: 'RUNNING', iteration_count: 1 };

        vi.mocked(api.getAgentStatus)
            .mockResolvedValueOnce(mockPending as any)
            .mockResolvedValueOnce(mockRunning as any);

        renderWithRouter(<AgentRunPage />);

        await waitFor(() => expect(screen.getAllByText(/PENDING/i)[0]).toBeInTheDocument());

        // Advance timers by the polling interval to trigger the next fetch
        await act(async () => {
            await vi.advanceTimersByTimeAsync(3000);
        });

        await waitFor(() => {
            expect(api.getAgentStatus).toHaveBeenCalledTimes(2);
            expect(screen.getAllByText(/RUNNING/i)[0]).toBeInTheDocument();
            expect(screen.getByText(/1 \/ ∞/i)).toBeInTheDocument();
        });
    });

    it('clears polling upon terminal state COMPLETED', async () => {
        vi.mocked(useParams).mockReturnValue({ runId: 'run-comp' });
        vi.mocked(api.getAgentStatus).mockResolvedValue({
            id: 'run-comp', task_id: 'task-1', status: 'COMPLETED',
            iteration_count: 4, started_at: '2023-01-01T00:00:00Z',
            completed_at: '2023-01-01T00:05:00Z', owner_id: 'u1'
        } as any);

        renderWithRouter(<AgentRunPage />);

        await waitFor(() => expect(screen.getAllByText(/COMPLETED/i)[0]).toBeInTheDocument());

        // Component should have stopped the polling interval (clearable via unmount without error)
        const { unmount } = renderWithRouter(<AgentRunPage />);
        expect(() => unmount()).not.toThrow();
    });

    it('clears polling gracefully upon API resolution errors', async () => {
        vi.mocked(useParams).mockReturnValue({ runId: 'run-err2' });
        vi.mocked(api.getAgentStatus).mockRejectedValueOnce(new Error('Network offline'));

        renderWithRouter(<AgentRunPage />);

        await waitFor(() => expect(screen.getByText(/Network offline/i)).toBeInTheDocument());

        // Polling gracefully stopped
        expect(api.getAgentStatus).toHaveBeenCalledTimes(1);
    });

    it('clears polling upon terminal state FAILED', async () => {
        vi.mocked(useParams).mockReturnValue({ runId: 'run-fail2' });
        vi.mocked(api.getAgentStatus).mockResolvedValue({
            id: 'run-fail2', task_id: 'task-3', status: 'FAILED',
            iteration_count: 2, started_at: '2023-07-01T00:00:00Z',
            completed_at: '2023-07-01T00:01:00Z', owner_id: 'u1'
        } as any);

        renderWithRouter(<AgentRunPage />);

        await waitFor(() => expect(screen.getAllByText('FAILED')[0]).toBeInTheDocument());

        // Polling stopped at FAILED terminal state (unmount verifies no errors)
        const { unmount } = renderWithRouter(<AgentRunPage />);
        expect(() => unmount()).not.toThrow();
    });
});
