import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Project, TaskCreate } from '../types';
import LoadingState from '../components/UI/LoadingState';
import ErrorState from '../components/UI/ErrorState';

const ProjectDetailsPage: React.FC = () => {
    const { projectId } = useParams<{ projectId: string }>();
    const navigate = useNavigate();
    const [project, setProject] = useState<Project | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Task creation form states
    const [taskDesc, setTaskDesc] = useState('');
    const [taskLoading, setTaskLoading] = useState(false);
    const [taskError, setTaskError] = useState<string | null>(null);

    useEffect(() => {
        const fetchProject = async () => {
            if (!projectId) return;
            try {
                const data = await api.getProject(projectId);
                setProject(data);
            } catch (err: any) {
                setError(err.message || 'Failed to fetch project details.');
            } finally {
                setLoading(false);
            }
        };

        fetchProject();
    }, [projectId]);

    const handleCreateTask = async (e: React.FormEvent) => {
        e.preventDefault();
        setTaskError(null);

        if (!taskDesc.trim() || !projectId) return;
        if (taskLoading) return; // Prevent duplicate submission

        setTaskLoading(true);
        try {
            const data: TaskCreate = {
                project_id: projectId,
                description: taskDesc.trim(),
            };
            const newTask = await api.createTask(data);
            navigate(`/tasks/${newTask.id}`);
        } catch (err: any) {
            setTaskError(err.message || 'Failed to create task');
            setTaskLoading(false);
        }
    };

    if (loading) return <LoadingState message="Loading project details..." />;
    if (error || !project) return <div style={{ padding: '2rem' }}><ErrorState message={error || 'Project not found'} /></div>;

    const blockStyle: React.CSSProperties = {
        backgroundColor: '#ffffff',
        padding: '1.5rem',
        borderRadius: '0.5rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        marginBottom: '1.5rem'
    };

    return (
        <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '800px', margin: '0 auto' }}>
            <Link to="/projects" style={{ color: '#3b82f6', textDecoration: 'none', display: 'inline-block', marginBottom: '1.5rem' }}>
                &larr; Back to Projects
            </Link>

            <div style={blockStyle}>
                <h1 style={{ margin: '0 0 0.5rem 0', color: '#111827' }}>{project.name}</h1>
                <p style={{ color: '#4b5563', fontSize: '1rem', marginBottom: '1.5rem' }}>
                    {project.description || 'No description provided.'}
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.875rem' }}>
                    <div>
                        <strong style={{ color: '#374151', display: 'block' }}>Local Repository Path</strong>
                        <span style={{ color: '#6b7280' }}>{project.repository_path || 'None'}</span>
                    </div>
                    <div>
                        <strong style={{ color: '#374151', display: 'block' }}>Remote Repository URL</strong>
                        {project.repository_url ? (
                            <a href={project.repository_url} target="_blank" rel="noreferrer" style={{ color: '#3b82f6' }}>{project.repository_url}</a>
                        ) : (
                            <span style={{ color: '#6b7280' }}>None</span>
                        )}
                    </div>
                    <div>
                        <strong style={{ color: '#374151', display: 'block' }}>Created At</strong>
                        <span style={{ color: '#6b7280' }}>{new Date(project.created_at).toLocaleString()}</span>
                    </div>
                    <div>
                        <strong style={{ color: '#374151', display: 'block' }}>Project ID</strong>
                        <span style={{ color: '#6b7280', fontFamily: 'monospace' }}>{project.id}</span>
                    </div>
                </div>
            </div>

            {/* Create Task Section */}
            <div style={blockStyle}>
                <h2 style={{ margin: '0 0 1rem 0', color: '#111827', fontSize: '1.25rem' }}>Create New Coding Task</h2>
                <p style={{ color: '#4b5563', fontSize: '0.875rem', marginBottom: '1rem' }}>
                    Submit a coding task for this project. After submission, you will be redirected to the Task Details page.
                </p>

                {taskError && (
                    <div style={{ color: '#991b1b', backgroundColor: '#fee2e2', padding: '0.75rem', borderRadius: '0.375rem', marginBottom: '1rem', fontSize: '0.875rem' }}>
                        {taskError}
                    </div>
                )}

                <form onSubmit={handleCreateTask}>
                    <div style={{ marginBottom: '1rem' }}>
                        <label
                            htmlFor="taskDesc"
                            style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#374151', marginBottom: '0.5rem' }}
                        >
                            Task Requirements *
                        </label>
                        <textarea
                            id="taskDesc"
                            value={taskDesc}
                            onChange={(e) => setTaskDesc(e.target.value)}
                            required
                            disabled={taskLoading}
                            style={{
                                width: '100%',
                                padding: '0.5rem',
                                boxSizing: 'border-box',
                                border: '1px solid #d1d5db',
                                borderRadius: '0.375rem',
                                minHeight: '120px',
                                fontFamily: 'inherit',
                                fontSize: '0.875rem',
                                resize: 'vertical',
                            }}
                            placeholder="Describe the coding task in detail, e.g. 'Create a Python function that returns the sum of two numbers.'"
                        />
                    </div>
                    <div style={{ display: 'flex', gap: '0.75rem' }}>
                        <button
                            type="submit"
                            disabled={taskLoading}
                            style={{
                                padding: '0.625rem 1.5rem',
                                backgroundColor: taskLoading ? '#93c5fd' : '#3b82f6',
                                color: '#ffffff',
                                border: 'none',
                                borderRadius: '0.375rem',
                                cursor: taskLoading ? 'not-allowed' : 'pointer',
                                fontWeight: 600,
                                fontSize: '0.875rem',
                            }}
                        >
                            {taskLoading ? 'Submitting...' : 'Submit Task'}
                        </button>
                    </div>
                </form>
            </div>

            {/* Task listing note */}
            <div style={{ ...blockStyle, backgroundColor: '#f9fafb' }}>
                <p style={{ margin: 0, fontSize: '0.875rem', color: '#6b7280' }}>
                    <strong>Note:</strong> Listing tasks by project is not supported by the current backend API.
                    Creating a task will redirect you to its Task Details view immediately.
                </p>
            </div>
        </div>
    );
};

export default ProjectDetailsPage;
