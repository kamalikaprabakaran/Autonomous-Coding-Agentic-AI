import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from '../pages/LoginPage';
import SignupPage from '../pages/SignupPage';
import { AuthProvider } from './AuthContext';
import ProtectedRoute from '../components/ProtectedRoute';
import * as firebaseAuth from 'firebase/auth';

vi.mock('firebase/app', () => {
    class FirebaseError extends Error {
        constructor(public code: string, message: string) {
            super(message);
        }
    }
    return {
        initializeApp: vi.fn(),
        getApps: vi.fn(() => []),
        FirebaseError,
    };
});

vi.mock('firebase/auth', () => ({
    getAuth: vi.fn(),
    onAuthStateChanged: vi.fn(),
    signInWithEmailAndPassword: vi.fn(),
    createUserWithEmailAndPassword: vi.fn(),
    signOut: vi.fn(),
}));

describe('Authentication UI Tests', () => {

    beforeEach(() => {
        vi.resetAllMocks();
    });

    const renderWithRouter = (ui: React.ReactElement) => {
        return render(
            <MemoryRouter>
                {ui}
            </MemoryRouter>
        );
    };

    it('renders Login page', () => {
        vi.mocked(firebaseAuth.onAuthStateChanged).mockImplementation((_: any, cb: any) => {
            cb(null);
            return vi.fn();
        });

        renderWithRouter(<AuthProvider><LoginPage /></AuthProvider>);
        expect(screen.getByRole('heading', { name: /Log In/i })).toBeInTheDocument();
        expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    });

    it('renders Signup page', () => {
        vi.mocked(firebaseAuth.onAuthStateChanged).mockImplementation((_: any, cb: any) => {
            cb(null);
            return vi.fn();
        });

        renderWithRouter(<AuthProvider><SignupPage /></AuthProvider>);
        expect(screen.getByRole('heading', { name: /Sign Up/i })).toBeInTheDocument();
        expect(screen.getByLabelText(/Confirm Password/i)).toBeInTheDocument();
    });

    it('displays error on failed login', async () => {
        vi.mocked(firebaseAuth.onAuthStateChanged).mockImplementation((_: any, cb: any) => {
            cb(null);
            return vi.fn();
        });

        // Mock rejection with a specific Firebase error code object
        vi.mocked(firebaseAuth.signInWithEmailAndPassword).mockRejectedValueOnce({ code: 'auth/invalid-credential' });

        renderWithRouter(<AuthProvider><LoginPage /></AuthProvider>);

        fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'test@test.com' } });
        fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'password' } });
        fireEvent.click(screen.getByRole('button', { name: /Log In/i }));

        await waitFor(() => {
            expect(screen.getByText(/Invalid email or password\./i)).toBeInTheDocument();
        });
    });

    it('redirects unauthenticated users from protected route', async () => {
        vi.mocked(firebaseAuth.onAuthStateChanged).mockImplementation((_: any, cb: any) => {
            cb(null); // Unauthenticated
            return vi.fn();
        });

        renderWithRouter(
            <AuthProvider>
                <ProtectedRoute>
                    <div>Protected Content</div>
                </ProtectedRoute>
            </AuthProvider>
        );

        // Protected content shouldn't be here. Due to memory router, it won't actually change URL but it shouldn't render children
        expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });

    it('renders protected child component for authenticated users', async () => {
        vi.mocked(firebaseAuth.onAuthStateChanged).mockImplementation((_: any, cb: any) => {
            cb({ uid: '123', email: 'test@example.com' }); // Authenticated
            return vi.fn();
        });

        renderWithRouter(
            <AuthProvider>
                <ProtectedRoute>
                    <div>Protected Content</div>
                </ProtectedRoute>
            </AuthProvider>
        );

        expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });
});
