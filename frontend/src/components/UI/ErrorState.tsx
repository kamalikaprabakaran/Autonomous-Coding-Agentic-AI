import React from 'react';

const ErrorState: React.FC<{ message?: string }> = ({ message = 'An error occurred' }) => {
    return (
        <div style={{ padding: '1rem', backgroundColor: '#fee2e2', color: '#991b1b', borderRadius: '0.375rem', marginBottom: '1rem' }}>
            <strong>Error:</strong> {message}
        </div>
    );
};

export default ErrorState;
