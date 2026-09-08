import React from 'react';
import { Link } from 'react-router-dom';
import { Project } from '../../types';

interface ProjectCardProps {
    project: Project;
}

const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
    return (
        <div style={{
            padding: '1.5rem',
            backgroundColor: '#ffffff',
            borderRadius: '0.5rem',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            height: '100%',
            fontFamily: 'sans-serif'
        }}>
            <div>
                <h3 style={{ margin: '0 0 0.5rem 0', color: '#111827', fontSize: '1.25rem' }}>
                    {project.name}
                </h3>
                <p style={{ color: '#4b5563', fontSize: '0.875rem', marginBottom: '1rem', flexGrow: 1 }}>
                    {project.description || 'No description provided.'}
                </p>
                <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '1rem' }}>
                    <div><strong>Created:</strong> {new Date(project.created_at).toLocaleDateString()}</div>
                    {project.repository_url && (
                        <div style={{ marginTop: '0.25rem' }}>
                            <strong>Repo:</strong> <a href={project.repository_url} target="_blank" rel="noreferrer" style={{ color: '#3b82f6', textDecoration: 'none' }}>{project.repository_url}</a>
                        </div>
                    )}
                </div>
            </div>

            <Link
                to={`/projects/${project.id}`}
                style={{
                    display: 'inline-block',
                    padding: '0.5rem 1rem',
                    backgroundColor: '#1f2937',
                    color: '#ffffff',
                    textDecoration: 'none',
                    borderRadius: '0.375rem',
                    textAlign: 'center',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    transition: 'background-color 0.2s'
                }}
            >
                View Details
            </Link>
        </div>
    );
};

export default ProjectCard;
