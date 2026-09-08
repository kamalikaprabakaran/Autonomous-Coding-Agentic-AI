import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';

const LoginPage: React.FC = () => {
    const { signIn } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            await signIn(email, password);
            navigate('/projects');
        } catch (err: any) {
            if (err?.code) {
                if (err.code === 'auth/invalid-credential') {
                    setError('Invalid email or password.');
                } else if (err.code === 'auth/too-many-requests') {
                    setError('Too many failed attempts. Try again later.');
                } else {
                    setError('Failed to log in. Please try again.');
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
            <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', color: '#111827' }}>Log In</h2>
            {error && (
                <div style={{ backgroundColor: '#fee2e2', color: '#991b1b', padding: '0.75rem', borderRadius: '0.375rem', marginBottom: '1rem' }}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '1rem' }}>
                    <label htmlFor="login-email" style={{ display: 'block', marginBottom: '0.5rem', color: '#374151' }}>Email</label>
                    <input
                        id="login-email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        style={inputStyle}
                        required
                        placeholder="you@example.com"
                    />
                </div>
                <div style={{ marginBottom: '1.5rem' }}>
                    <label htmlFor="login-password" style={{ display: 'block', marginBottom: '0.5rem', color: '#374151' }}>Password</label>
                    <input
                        id="login-password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={inputStyle}
                        required
                    />
                </div>
                <button type="submit" style={buttonStyle} disabled={loading}>
                    {loading ? 'Logging in...' : 'Log In'}
                </button>
            </form>
            <div style={{ textAlign: 'center', marginTop: '1.5rem', color: '#6b7280' }}>
                Don't have an account? <Link to="/signup" style={{ color: '#3b82f6', textDecoration: 'none' }}>Sign up</Link>
            </div>
        </div>
    );
};

export default LoginPage;
