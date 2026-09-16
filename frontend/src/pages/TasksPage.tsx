import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api, ApiError } from '../services/api';
import { Task } from '../types';
import LoadingState from '../components/UI/LoadingState';
import ErrorState from '../components/UI/ErrorState';

const TasksPage: React.FC = () => {
    const { taskId } = useParams<{ taskId?: string }>();
    const [task, setTask] = useState<Task | null>(null);
    const [loading, setLoading] = useState(false);
    const [startingAgent, setStartingAgent] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [errorStatus, setErrorStatus] = useState<number | null>(null);
    const [searchInput, setSearchInput] = useState('');

    useEffect(() => {
        const fetchTask = async () => {
            if (!taskId) return;
            setLoading(true);
            setError(null);
            setErrorStatus(null);
            try {
                const data = await api.getTask(taskId);
                setTask(data);
            } catch (err: any) {
                if (err instanceof ApiError) {
                    setErrorStatus(err.status);
                }
                setError(err.message || 'Failed to fetch task details.');
                setTask(null);
            } finally {
                setLoading(false);
            }
        };

        fetchTask();
    }, [taskId]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (searchInput.trim()) {
            window.location.href = `/tasks/${searchInput.trim()}`;
        }
    };

    const getErrorMessage = () => {
        if (errorStatus === 404) return 'Task not found. It may have been deleted or the ID is incorrect.';
        if (errorStatus === 403) return 'You do not have permission to view this task.';
        if (errorStatus === 401) return 'Authentication required.';
        return error || 'An unexpected error occurred. Please try again.';
    };

    const handleStartAgent = async () => {
        if (!task) return;
        setStartingAgent(true);
        setError(null);
        try {
            const run = await api.startAgent(task.id);
            window.location.href = `/agent/${run.id}`;
        } catch (err: any) {
            setError(err.message || 'Failed to start agent.');
        } finally {
            setStartingAgent(false);
        }
    };

    // No taskId — show search form
    if (!taskId) {
        return (
            <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '600px', margin: '0 auto' }}>
                <div style={{ backgroundColor: '#ffffff', padding: '2rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                    <h2 style={{ marginTop: 0, color: '#111827' }}>Find Task</h2>
                    <p style={{ color: '#4b5563', marginBottom: '1.5rem' }}>
                        Enter a Task ID to view its details. Tasks are created from the Project Details page.
                    </p>
                    <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem' }}>
                        <input
                            type="text"
                            value={searchInput}
                            onChange={(e) => setSearchInput(e.target.value)}
                            placeholder="Enter Task ID (UUID)"
                            style={{ flexGrow: 1, padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
                            required
                        />
                        <button
                            type="submit"
                            style={{
                                padding: '0.75rem 1.5rem',
                                backgroundColor: '#3b82f6',
                                color: '#ffffff',
                                border: 'none',
                                borderRadius: '0.375rem',
                                cursor: 'pointer',
                                fontWeight: 600
                            }}
                        >
                            Search
                        </button>
                    </form>
                </div>
            </div>
        );
    }

    if (loading) return <LoadingState message="Loading Task details..." />;

    if (error) {
        return (
            <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
                <Link to="/tasks" style={{ color: '#3b82f6', textDecoration: 'none', display: 'inline-block', marginBottom: '1.5rem' }}>
                    &larr; Back to Task Search
                </Link>
                <ErrorState message={getErrorMessage()} />
            </div>
        );
    }

    if (!task) return null;

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'PENDING': return { bg: '#fef3c7', text: '#92400e' };
            case 'RUNNING': return { bg: '#dbeafe', text: '#1e3a8a' };
            case 'COMPLETED': return { bg: '#d1fae5', text: '#065f46' };
            case 'FAILED': return { bg: '#fee2e2', text: '#991b1b' };
            default: return { bg: '#f3f4f6', text: '#374151' };
        }
    };

    const statusStyle = getStatusColor(task.status);

    return (
        <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '800px', margin: '0 auto' }}>
            <div style={{ marginBottom: '1.5rem' }}>
                <Link to={`/projects/${task.project_id}`} style={{ color: '#3b82f6', textDecoration: 'none' }}>
                    &larr; Back to Parent Project
                </Link>
            </div>

            {/* Task Details Card */}
            <div style={{
                backgroundColor: '#ffffff',
                padding: '1.5rem',
                borderRadius: '0.5rem',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                marginBottom: '1.5rem'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                    <h1 style={{ margin: 0, color: '#111827', fontSize: '1.5rem' }}>Task Details</h1>
                    <span style={{
                        padding: '0.25rem 0.75rem',
                        borderRadius: '9999px',
                        fontSize: '0.75rem',
                        fontWeight: 'bold',
                        backgroundColor: statusStyle.bg,
                        color: statusStyle.text
                    }}>
                        {task.status}
                    </span>
                </div>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'minmax(120px, auto) 1fr',
                    gap: '1rem 2rem',
                    fontSize: '0.875rem'
                }}>
                    <strong style={{ color: '#374151' }}>Task ID</strong>
                    <span style={{ color: '#6b7280', fontFamily: 'monospace' }}>{task.id}</span>

                    <strong style={{ color: '#374151' }}>Project ID</strong>
                    <span style={{ color: '#6b7280', fontFamily: 'monospace' }}>
                        <Link to={`/projects/${task.project_id}`} style={{ color: '#3b82f6', textDecoration: 'none' }}>
                            {task.project_id}
                        </Link>
                    </span>

                    <strong style={{ color: '#374151' }}>Created At</strong>
                    <span style={{ color: '#6b7280' }}>{new Date(task.created_at).toLocaleString()}</span>

                    <strong style={{ color: '#374151' }}>Description</strong>
                    <span style={{
                        color: '#111827',
                        whiteSpace: 'pre-wrap',
                        backgroundColor: '#f9fafb',
                        padding: '1rem',
                        borderRadius: '0.375rem',
                        border: '1px solid #e5e7eb',
                        display: 'block'
                    }}>
                        {task.description}
                    </span>
                </div>
            </div>

            {/* Agent Execution Section */}
            <div style={{
                backgroundColor: '#ffffff',
                padding: '1.5rem',
                borderRadius: '0.5rem',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
            }}>
                <h2 style={{ margin: '0 0 1rem 0', color: '#111827', fontSize: '1.25rem' }}>Agent Execution</h2>

                <div style={{ marginBottom: '1.5rem' }}>
                    <button
                        onClick={handleStartAgent}
                        disabled={startingAgent || task.status === 'COMPLETED'}
                        style={{
                            padding: '0.75rem 1.5rem',
                            backgroundColor: startingAgent ? '#9ca3af' : '#10b981',
                            color: '#ffffff',
                            border: 'none',
                            borderRadius: '0.375rem',
                            cursor: startingAgent ? 'not-allowed' : 'pointer',
                            fontWeight: 'bold',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                        }}
                    >
                        {startingAgent ? 'Starting Agent...' : 'Start New Agent Run'}
                    </button>
                    {error && startingAgent === false && (
                        <p style={{ color: '#ef4444', fontSize: '0.875rem', marginTop: '0.5rem' }}>{error}</p>
                    )}
                </div>

                <p style={{ margin: '0 0 1rem 0', fontSize: '0.875rem', color: '#4b5563' }}>
                    If a run has already been created for this task, enter its Run ID below to check its status:
                </p>

                <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.75rem' }}>
                    <input
                        type="text"
                        value={searchInput}
                        onChange={(e) => setSearchInput(e.target.value)}
                        placeholder="Enter Agent Run ID to inspect status"
                        style={{ flexGrow: 1, padding: '0.5rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
                    />
                    <button
                        type="submit"
                        style={{
                            padding: '0.5rem 1.5rem',
                            backgroundColor: '#111827',
                            color: '#ffffff',
                            border: 'none',
                            borderRadius: '0.375rem',
                            cursor: 'pointer',
                            fontWeight: 'bold'
                        }}
                    >
                        View Run
                    </button>
                </form>
            </div>
        </div>
    );
};

export default TasksPage;
