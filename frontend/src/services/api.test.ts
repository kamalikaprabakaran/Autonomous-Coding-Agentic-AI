import { vi, describe, it, expect, beforeEach } from 'vitest';
import { api } from './api';
import { auth } from './firebase';

vi.mock('firebase/app', () => ({
    initializeApp: vi.fn(),
    getApps: vi.fn(() => []),
}));

vi.mock('./firebase', () => ({
    auth: {
        currentUser: null,
        signOut: vi.fn(),
    }
}));

describe('API Token Handling Tests', () => {

    beforeEach(() => {
        vi.resetAllMocks();
        global.fetch = vi.fn();
        // @ts-ignore
        delete window.location;
        // @ts-ignore
        window.location = { href: '' };
    });

    it('does not attach token when unauthenticated', async () => {
        (auth as any).currentUser = null;
        const mockFetch = vi.mocked(global.fetch).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ status: 'healthy' })
        } as any);

        await api.getHealth();

        const fetchArgs = mockFetch.mock.calls[0];
        expect(fetchArgs[1]?.headers).not.toHaveProperty('Authorization');
    });

    it('attaches token when authenticated user makes API call', async () => {
        const mockGetIdToken = vi.fn().mockResolvedValue('fake-firebase-token');

        // @ts-ignore
        auth.currentUser = {
            getIdToken: mockGetIdToken
        };

        const mockFetch = vi.mocked(global.fetch).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ status: 'healthy' })
        } as any);

        await api.getHealth();

        const fetchArgs = mockFetch.mock.calls[0];
        const headers: any = fetchArgs[1]?.headers;
        expect(headers['Authorization']).toBe('Bearer fake-firebase-token');
    });

    it('handles 401 response correctly by signing out and redirecting', async () => {
        (auth as any).currentUser = null;

        vi.mocked(global.fetch).mockResolvedValueOnce({
            ok: false,
            status: 401,
            statusText: 'Unauthorized'
        } as any);

        await expect(api.getHealth()).rejects.toThrow('Network response was not ok: Unauthorized');
        expect(auth.signOut).toHaveBeenCalled();
        expect(window.location.href).toBe('/login');
    });
});
