import React from 'react';
import { useAuth } from '../../context/AuthContext';
import AdminLogin from './AdminLogin';
import AdminDashboard from './AdminDashboard';

const AdminPanelWrapper = () => {
  const { user, token, loading, logout, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: '#000',
        color: '#00ff00'
      }}>
        <h2>🔐 Authenticating...</h2>
      </div>
    );
  }

  if (!isAuthenticated()) {
    return <AdminLogin />;
  }

  return (
    <AdminDashboard 
      token={token} 
      onLogout={logout} 
    />
  );
};

export default AdminPanelWrapper;
