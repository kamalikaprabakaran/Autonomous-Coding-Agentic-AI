import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Project } from '../types';
import ProjectCard from '../components/Projects/ProjectCard';
import CreateProjectModal from '../components/Projects/CreateProjectModal';
import LoadingState from '../components/UI/LoadingState';
import ErrorState from '../components/UI/ErrorState';

const ProjectsPage: React.FC = () => {
    const [projects, setProjects] = useState<Project[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
        const fetchProjects = async () => {
            try {
                const data = await api.getProjects();
                setProjects(data);
            } catch (err: any) {
                setError(err.message || 'Failed to fetch projects.');
            } finally {
                setLoading(false);
            }
        };

        fetchProjects();
    }, []);

    const handleProjectCreated = (newProject: Project) => {
        setProjects([newProject, ...projects]);
        setShowModal(false);
    };

    if (loading) return <LoadingState message="Loading your dashboard..." />;
    if (error) return <div style={{ padding: '2rem' }}><ErrorState message={error} /></div>;

    return (
        <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1 style={{ margin: 0, color: '#111827' }}>Dashboard</h1>
                    <p style={{ margin: 0, color: '#6b7280' }}>Total Projects: {projects.length}</p>
                </div>
                <button
                    onClick={() => setShowModal(true)}
                    style={{
                        padding: '0.75rem 1.5rem',
                        backgroundColor: '#3b82f6',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '0.375rem',
                        fontWeight: 'bold',
                        cursor: 'pointer',
                        boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                    }}
                >
                    Create Project
                </button>
            </div>

            {projects.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '4rem 2rem', backgroundColor: '#f9fafb', borderRadius: '0.5rem', border: '2px dashed #e5e7eb' }}>
                    <h3 style={{ marginTop: 0, color: '#374151' }}>No projects yet</h3>
                    <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>Get started by creating your first project.</p>
                    <button
                        onClick={() => setShowModal(true)}
                        style={{ padding: '0.5rem 1rem', backgroundColor: '#111827', color: '#fff', border: 'none', borderRadius: '0.375rem', cursor: 'pointer' }}
                    >
                        Create Project
                    </button>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
                    {projects.map((project) => (
                        <ProjectCard key={project.id} project={project} />
                    ))}
                </div>
            )}

            {showModal && (
                <CreateProjectModal
                    onClose={() => setShowModal(false)}
                    onProjectCreated={handleProjectCreated}
                />
            )}
        </div>
    );
};

export default ProjectsPage;
