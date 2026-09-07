import React from 'react';
import { NavLink } from 'react-router-dom';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
        <div style={{ display: 'flex', minHeight: '100vh', fontFamily: 'sans-serif' }}>
            <Sidebar />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Header />
                <main style={{ padding: '2rem', flex: 1, backgroundColor: '#f9fafb' }}>
                    {children}
                </main>
            </div>
        </div>
    );
};

const Sidebar: React.FC = () => {
    const linkStyle = {
        display: 'block',
        padding: '0.75rem 1rem',
        color: '#374151',
        textDecoration: 'none',
        borderRadius: '0.375rem',
        marginBottom: '0.5rem',
    };

    const activeStyle = {
        ...linkStyle,
        backgroundColor: '#e5e7eb',
        fontWeight: 'bold',
    };

    return (
        <aside style={{ width: '250px', backgroundColor: '#f3f4f6', padding: '1rem', borderRight: '1px solid #e5e7eb' }}>
            <div style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '2rem', color: '#111827' }}>
                Agentic AI
            </div>
            <nav>
                <NavLink to="/" style={({ isActive }) => isActive ? activeStyle : linkStyle}>
                    Home
                </NavLink>
                <NavLink to="/projects" style={({ isActive }) => isActive ? activeStyle : linkStyle}>
                    Projects
                </NavLink>
                <NavLink to="/tasks" style={({ isActive }) => isActive ? activeStyle : linkStyle}>
                    Tasks
                </NavLink>
                <NavLink to="/agent" style={({ isActive }) => isActive ? activeStyle : linkStyle}>
                    Agent Runs
                </NavLink>
            </nav>
        </aside>
    );
};

const Header: React.FC = () => {
    return (
        <header style={{ height: '60px', backgroundColor: '#ffffff', borderBottom: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', padding: '0 2rem' }}>
            <h2 style={{ margin: 0, fontSize: '1.125rem', color: '#374151', fontWeight: 500 }}>Dashboard</h2>
        </header>
    );
};

export default Layout;
