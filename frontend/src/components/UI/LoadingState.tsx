import React from 'react';

const LoadingState: React.FC<{ message?: string }> = ({ message = 'Loading...' }) => {
    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '2rem', color: '#6b7280' }}>
            <span>{message}</span>
        </div>
    );
};

export default LoadingState;
