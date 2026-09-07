import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
import App from './App';
import * as apiService from './services/api';

vi.mock('./services/api', () => ({
    api: {
        getHealth: vi.fn(),
    },
}));

describe('Frontend Application Foundation', () => {
    it('renders Layout and Sidebar correctly', async () => {
        // Explicitly mocking for Home rendering
        vi.mocked(apiService.api.getHealth).mockResolvedValueOnce({ status: 'healthy' });

        render(<App />);

        expect(screen.getByText('Agentic AI')).toBeInTheDocument();
        expect(screen.getByText('Home')).toBeInTheDocument();
        expect(screen.getByText('Projects')).toBeInTheDocument();
        expect(screen.getByText('Tasks')).toBeInTheDocument();
        expect(screen.getByText('Agent Runs')).toBeInTheDocument();

        await waitFor(() => {
            expect(screen.getByText(/Backend Connected/i)).toBeInTheDocument();
        });
    });

    it('renders HomePage appropriately and mocks health API successfully', async () => {
        vi.mocked(apiService.api.getHealth).mockResolvedValueOnce({ status: 'healthy' });

        // Test the Home page mounting natively without routing isolation,
        // since '/' is default
        render(<App />);

        expect(screen.getByText('Welcome to Autonomous Agentic AI')).toBeInTheDocument();
        expect(screen.getByText('Checking backend health...')).toBeInTheDocument();

        await waitFor(() => {
            expect(screen.getByText(/Backend Connected/i)).toBeInTheDocument();
            expect(screen.getByText(/Status: healthy/i)).toBeInTheDocument();
        });
    });

    it('renders API connection error state', async () => {
        vi.mocked(apiService.api.getHealth).mockRejectedValueOnce(new Error('Network offline'));

        render(<App />);

        await waitFor(() => {
            expect(screen.getByText(/Backend unavailable: Network offline/i)).toBeInTheDocument();
        });
    });
});
