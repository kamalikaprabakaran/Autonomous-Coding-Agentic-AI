import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';

interface PublicRouteProps {
    children: React.ReactNode;
}

const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
    const { currentUser, loading } = useAuth();

    if (loading) {
        return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading...</div>;
    }

    if (currentUser) {
        return <Navigate to="/projects" replace />;
    }

    return <>{children}</>;
};

export default PublicRoute;
