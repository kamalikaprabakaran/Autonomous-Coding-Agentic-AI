import React, { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { AgentRun } from '../types';
import LoadingState from '../components/UI/LoadingState';
import ErrorState from '../components/UI/ErrorState';

const POLL_INTERVAL_MS = 3000;

const AgentRunPage: React.FC = () => {
    const { runId } = useParams<{ runId?: string }>();
    const [agentRun, setAgentRun] = useState<AgentRun | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [searchInput, setSearchInput] = useState('');
    const intervalRef = useRef<number | null>(null);

    const stopPolling = () => {
        if (intervalRef.current !== null) {
            try {
                clearInterval(intervalRef.current);
            } catch {
                // Silently handle if clearInterval is unavailable (test cleanup timing)
            }
            intervalRef.current = null;
        }
    };

    const fetchStatus = async (id: string, isPolling = false) => {
        if (!isPolling) setLoading(true);
        try {
            const data = await api.getAgentStatus(id);
            setAgentRun(data);
            setError(null);

            // Stop polling when a terminal state is reached
            if (data.status === 'COMPLETED' || data.status === 'FAILED') {
                stopPolling();
            }
        } catch (err: any) {
            setError(err.message || 'Failed to fetch Agent Run details.');
            if (!isPolling) setAgentRun(null);

            // Stop polling on hard error
            stopPolling();
        } finally {
            if (!isPolling) setLoading(false);
        }
    };

    useEffect(() => {
        if (!runId) return;

        // Initial fetch
        fetchStatus(runId);

        // Start polling for live status
        intervalRef.current = setInterval(() => {
            fetchStatus(runId, true);
        }, POLL_INTERVAL_MS) as unknown as number;

        // Cleanup on unmount or runId change
        return () => {
            stopPolling();
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [runId]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (searchInput.trim()) {
            window.location.href = `/agent/${searchInput.trim()}`;
        }
    };

    if (!runId) {
        return (
            <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '600px', margin: '0 auto' }}>
                <div style={{ backgroundColor: '#ffffff', padding: '2rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                    <h2 style={{ marginTop: 0, color: '#111827' }}>Agent Execution Status Analyzer</h2>
                    <p style={{ color: '#4b5563', marginBottom: '0.75rem' }}>
                        To monitor a coding agent execution, provide its Run ID below.
                    </p>
                    <div style={{ backgroundColor: '#fef3c7', color: '#92400e', padding: '0.75rem', borderRadius: '0.375rem', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
                        <strong>Note:</strong> There is currently no REST endpoint to <em>start</em> an agent run from the frontend.
                        Agent runs are initiated internally by the system. You can inspect an existing run using its Run ID.
                    </div>
                    <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem' }}>
                        <input
                            type="text"
                            value={searchInput}
                            onChange={(e) => setSearchInput(e.target.value)}
                            placeholder="Enter Agent Run ID"
                            style={{ flexGrow: 1, padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
                            required
                        />
                        <button type="submit" style={{ padding: '0.75rem 1.5rem', backgroundColor: '#10b981', color: '#ffffff', border: 'none', borderRadius: '0.375rem', cursor: 'pointer', fontWeight: 'bold' }}>
                            Monitor Run
                        </button>
                    </form>
                </div>
            </div>
        );
    }

    if (loading && !agentRun) return <LoadingState message="Connecting to execution sandbox..." />;

    // Hard error blocking state (initial load failure)
    if (error && !agentRun) return <div style={{ padding: '2rem' }}><ErrorState message={error || 'Run not found'} /></div>;

    if (!agentRun) return null;

    const getStatusStyle = (status: string) => {
        switch (status) {
            case 'PENDING': return { bg: '#fef3c7', text: '#92400e', icon: '⏳', label: 'Waiting for agent execution' };
            case 'RUNNING': return { bg: '#dbeafe', text: '#1e3a8a', icon: '⚙️', label: 'Agent is working' };
            case 'COMPLETED': return { bg: '#d1fae5', text: '#065f46', icon: '✅', label: 'Agent completed successfully' };
            case 'FAILED': return { bg: '#fee2e2', text: '#991b1b', icon: '❌', label: 'Agent execution failed' };
            default: return { bg: '#f3f4f6', text: '#374151', icon: '❔', label: 'Unknown status' };
        }
    };

    const statusStyle = getStatusStyle(agentRun.status);
    const isTerminal = agentRun.status === 'COMPLETED' || agentRun.status === 'FAILED';

    return (
        <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '800px', margin: '0 auto' }}>
            <div style={{ marginBottom: '1.5rem' }}>
                <Link to={`/tasks/${agentRun.task_id}`} style={{ color: '#3b82f6', textDecoration: 'none' }}>
                    &larr; Back to Parent Task
                </Link>
            </div>

            <div style={{
                backgroundColor: '#ffffff',
                padding: '1.5rem',
                borderRadius: '0.5rem',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                borderTop: `4px solid ${statusStyle.text}`
            }}>
                {error && <div style={{ marginBottom: '1rem' }}><ErrorState message={`Polling warning: ${error}`} /></div>}

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                    <div>
                        <h1 style={{ margin: '0 0 0.25rem 0', color: '#111827', fontSize: '1.5rem' }}>Agent Execution Details</h1>
                        <span style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                            {statusStyle.label}
                        </span>
                    </div>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem 1rem',
                        borderRadius: '9999px',
                        backgroundColor: statusStyle.bg,
                        color: statusStyle.text,
                        fontWeight: 'bold'
                    }}>
                        <span>{statusStyle.icon}</span>
                        <span>{agentRun.status}</span>
                        {!isTerminal && (
                            <span
                                className="animate-pulse"
                                style={{
                                    width: '8px',
                                    height: '8px',
                                    backgroundColor: statusStyle.text,
                                    borderRadius: '50%',
                                    display: 'inline-block',
                                    marginLeft: '0.25rem'
                                }}
                            />
                        )}
                    </div>
                </div>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'minmax(140px, auto) 1fr',
                    gap: '1rem 2rem',
                    fontSize: '0.875rem',
                    backgroundColor: '#f9fafb',
                    padding: '1.5rem',
                    borderRadius: '0.375rem',
                    border: '1px solid #e5e7eb'
                }}>
                    <strong style={{ color: '#374151' }}>Agent Run ID</strong>
                    <span style={{ color: '#6b7280', fontFamily: 'monospace' }}>{agentRun.id}</span>

                    <strong style={{ color: '#374151' }}>Parent Task ID</strong>
                    <span style={{ color: '#6b7280', fontFamily: 'monospace' }}>
                        <Link to={`/tasks/${agentRun.task_id}`} style={{ color: '#3b82f6', textDecoration: 'none' }}>
                            {agentRun.task_id}
                        </Link>
                    </span>

                    <strong style={{ color: '#374151' }}>Iterations Complete</strong>
                    <span style={{ color: '#111827', fontWeight: 500 }}>{agentRun.iteration_count} / ∞</span>

                    <strong style={{ color: '#374151' }}>Started At</strong>
                    <span style={{ color: '#6b7280' }}>{new Date(agentRun.started_at).toLocaleString()}</span>

                    <strong style={{ color: '#374151' }}>Completed At</strong>
                    <span style={{ color: '#6b7280' }}>
                        {agentRun.completed_at ? new Date(agentRun.completed_at).toLocaleString() : '—'}
                    </span>

                    {agentRun.duration_seconds !== undefined && agentRun.duration_seconds > 0 && (
                        <>
                            <strong style={{ color: '#374151' }}>Execution Duration</strong>
                            <span style={{ color: '#6b7280' }}>{agentRun.duration_seconds.toFixed(2)}s</span>
                        </>
                    )}

                    {agentRun.error_summary && (
                        <>
                            <strong style={{ color: '#991b1b' }}>Error Summary</strong>
                            <span style={{ color: '#ef4444', whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                                {agentRun.error_summary}
                            </span>
                        </>
                    )}

                    <strong style={{ color: '#374151' }}>Live Updates</strong>
                    <span style={{ color: isTerminal ? '#065f46' : '#2563eb' }}>
                        {isTerminal ? 'Polling concluded.' : 'Polling for status updates every 3s...'}
                    </span>
                </div>
            </div>

            <style>
                {`
                @keyframes pulse-animation { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
                .animate-pulse { animation: pulse-animation 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
                `}
            </style>
        </div>
    );
};

export default AgentRunPage;
