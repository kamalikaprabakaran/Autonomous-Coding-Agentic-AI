import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import LoadingState from '../components/UI/LoadingState';
import ErrorState from '../components/UI/ErrorState';

const HomePage: React.FC = () => {
    const [health, setHealth] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const checkHealth = async () => {
            try {
                const data = await api.getHealth();
                setHealth(data.status);
            } catch (err: any) {
                setError(err.message || 'Unknown error');
            } finally {
                setLoading(false);
            }
        };
        checkHealth();
    }, []);

    return (
        <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem' }}>Welcome to Autonomous Agentic AI</h1>

            <div style={{ padding: '1.5rem', backgroundColor: '#ffffff', borderRadius: '0.375rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Backend Connection Status</h2>

                {loading && <LoadingState message="Checking backend health..." />}
                {error && <ErrorState message={`Backend unavailable: ${error}`} />}
                {health && (
                    <div style={{ display: 'flex', alignItems: 'center', color: '#166534', backgroundColor: '#dcfce7', padding: '1rem', borderRadius: '0.375rem' }}>
                        <span style={{ marginRight: '0.5rem', fontSize: '1.5rem' }}>✓</span>
                        Backend Connected (Status: {health})
                    </div>
                )}
            </div>
        </div>
    );
};

export default HomePage;
