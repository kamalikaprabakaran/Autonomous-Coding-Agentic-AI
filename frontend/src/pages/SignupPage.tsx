import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';

const SignupPage: React.FC = () => {
    const { signUp } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            setLoading(false);
            return;
        }

        try {
            await signUp(email, password);
            navigate('/projects');
        } catch (err: any) {
            if (err?.code) {
                if (err.code === 'auth/email-already-in-use') {
                    setError('Email is already in use.');
                } else if (err.code === 'auth/weak-password') {
                    setError('Password must be at least 6 characters.');
                } else {
                    setError('Failed to create an account. Please try again.');
                }
            } else {
                setError('An unexpected error occurred.');
            }
        } finally {
            setLoading(false);
        }
    };

    const containerStyle: React.CSSProperties = {
        maxWidth: '400px',
        margin: '4rem auto',
        padding: '2rem',
        backgroundColor: '#ffffff',
        borderRadius: '0.5rem',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        fontFamily: 'sans-serif'
    };

    const inputStyle: React.CSSProperties = {
        width: '100%',
        padding: '0.75rem',
        marginBottom: '1rem',
        border: '1px solid #d1d5db',
        borderRadius: '0.375rem',
        boxSizing: 'border-box'
    };

    const buttonStyle: React.CSSProperties = {
        width: '100%',
        padding: '0.75rem',
        backgroundColor: '#111827',
        color: '#ffffff',
        border: 'none',
        borderRadius: '0.375rem',
        cursor: loading ? 'not-allowed' : 'pointer',
        fontWeight: 'bold',
        opacity: loading ? 0.7 : 1
    };

    return (
        <div style={containerStyle}>
            <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', color: '#111827' }}>Sign Up</h2>
            {error && (
                <div style={{ backgroundColor: '#fee2e2', color: '#991b1b', padding: '0.75rem', borderRadius: '0.375rem', marginBottom: '1rem' }}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '1rem' }}>
                    <label htmlFor="signup-email" style={{ display: 'block', marginBottom: '0.5rem', color: '#374151' }}>Email</label>
                    <input
                        id="signup-email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        style={inputStyle}
                        required
                        placeholder="you@example.com"
                    />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                    <label htmlFor="signup-password" style={{ display: 'block', marginBottom: '0.5rem', color: '#374151' }}>Password</label>
                    <input
                        id="signup-password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={inputStyle}
                        required
                    />
                </div>
                <div style={{ marginBottom: '1.5rem' }}>
                    <label htmlFor="signup-confirm-password" style={{ display: 'block', marginBottom: '0.5rem', color: '#374151' }}>Confirm Password</label>
                    <input
                        id="signup-confirm-password"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        style={inputStyle}
                        required
                    />
                </div>
                <button type="submit" style={buttonStyle} disabled={loading}>
                    {loading ? 'Creating Account...' : 'Sign Up'}
                </button>
            </form>
            <div style={{ textAlign: 'center', marginTop: '1.5rem', color: '#6b7280' }}>
                Already have an account? <Link to="/login" style={{ color: '#3b82f6', textDecoration: 'none' }}>Log in</Link>
            </div>
        </div>
    );
};

export default SignupPage;
