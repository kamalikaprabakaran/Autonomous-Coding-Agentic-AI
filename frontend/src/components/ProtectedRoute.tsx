import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';

interface ProtectedRouteProps {
    children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    const { currentUser, loading } = useAuth();

    if (loading) {
        return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading...</div>;
    }

    if (!currentUser) {
        return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
};

export default ProtectedRoute;
