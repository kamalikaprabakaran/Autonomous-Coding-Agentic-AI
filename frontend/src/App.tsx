import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import HomePage from './pages/HomePage';
import ProjectsPage from './pages/ProjectsPage';
import TasksPage from './pages/TasksPage';
import AgentPage from './pages/AgentPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import { AuthProvider } from './auth/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import PublicRoute from './components/PublicRoute';

const App: React.FC = () => {
    return (
        <AuthProvider>
            <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
                <Layout>
                    <Routes>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
                        <Route path="/signup" element={<PublicRoute><SignupPage /></PublicRoute>} />
                        <Route path="/projects" element={<ProtectedRoute><ProjectsPage /></ProtectedRoute>} />
                        <Route path="/tasks" element={<ProtectedRoute><TasksPage /></ProtectedRoute>} />
                        <Route path="/agent" element={<ProtectedRoute><AgentPage /></ProtectedRoute>} />
                    </Routes>
                </Layout>
            </BrowserRouter>
        </AuthProvider>
    );
};

export default App;
