import React, { useState } from 'react';
import { api } from '../../services/api';
import { Project, ProjectCreate } from '../../types';

interface CreateProjectModalProps {
    onClose: () => void;
    onProjectCreated: (project: Project) => void;
}

const CreateProjectModal: React.FC<CreateProjectModalProps> = ({ onClose, onProjectCreated }) => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [repoPath, setRepoPath] = useState('');
    const [repoUrl, setRepoUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (!name.trim()) {
            setError('Project name is required.');
            return;
        }

        setLoading(true);
        try {
            const data: ProjectCreate = {
                name: name.trim(),
                description: description.trim() || undefined,
                repository_path: repoPath.trim() || null,
                repository_url: repoUrl.trim() || null
            };
            const newProject = await api.createProject(data);
            onProjectCreated(newProject);
        } catch (err: any) {
            setError(err.message || 'Failed to create project');
        } finally {
            setLoading(false);
        }
    };

    const overlayStyle: React.CSSProperties = {
        position: 'fixed',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 50
    };

    const modalStyle: React.CSSProperties = {
        backgroundColor: '#ffffff',
        padding: '2rem',
        borderRadius: '0.5rem',
        width: '100%',
        maxWidth: '500px',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
        fontFamily: 'sans-serif'
    };

    const inputStyle: React.CSSProperties = {
        width: '100%',
        padding: '0.5rem',
        marginTop: '0.25rem',
        marginBottom: '1rem',
        border: '1px solid #d1d5db',
        borderRadius: '0.375rem',
        boxSizing: 'border-box'
    };

    return (
        <div style={overlayStyle}>
            <div style={modalStyle}>
                <h2 style={{ marginTop: 0, marginBottom: '1rem', color: '#111827' }}>Create New Project</h2>

                {error && <div style={{ color: '#991b1b', backgroundColor: '#fee2e2', padding: '0.75rem', borderRadius: '0.375rem', marginBottom: '1rem' }}>{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div>
                        <label htmlFor="project-name" style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#374151' }}>Project Name *</label>
                        <input
                            id="project-name"
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            style={inputStyle}
                            required
                        />
                    </div>
                    <div>
                        <label htmlFor="project-desc" style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#374151' }}>Description</label>
                        <textarea
                            id="project-desc"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            style={{ ...inputStyle, minHeight: '80px', resize: 'vertical' }}
                        />
                    </div>
                    <div>
                        <label htmlFor="project-repo-path" style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#374151' }}>Local Repository Path</label>
                        <input
                            id="project-repo-path"
                            type="text"
                            value={repoPath}
                            onChange={(e) => setRepoPath(e.target.value)}
                            placeholder="/path/to/local/repo"
                            style={inputStyle}
                        />
                    </div>
                    <div>
                        <label htmlFor="project-repo-url" style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#374151' }}>Repository URL</label>
                        <input
                            id="project-repo-url"
                            type="url"
                            value={repoUrl}
                            onChange={(e) => setRepoUrl(e.target.value)}
                            placeholder="https://github.com/..."
                            style={inputStyle}
                        />
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                        <button
                            type="button"
                            onClick={onClose}
                            style={{ padding: '0.5rem 1rem', backgroundColor: '#ffffff', border: '1px solid #d1d5db', borderRadius: '0.375rem', cursor: 'pointer', color: '#374151' }}
                            disabled={loading}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            style={{ padding: '0.5rem 1rem', backgroundColor: '#3b82f6', color: '#ffffff', border: 'none', borderRadius: '0.375rem', cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1 }}
                            disabled={loading}
                        >
                            {loading ? 'Creating...' : 'Create Project'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateProjectModal;
