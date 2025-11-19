import React, { useState, useEffect } from 'react';
import AdminLogin from './AdminLogin';
import AdminDashboard from './AdminDashboard';

const AdminPanelWrapper = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(null);
  const [adminId, setAdminId] = useState(null);

  // Check for existing token on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('admin_token');
    const savedAdminId = localStorage.getItem('admin_id');
    
    if (savedToken && savedAdminId) {
      setToken(savedToken);
      setAdminId(savedAdminId);
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (newToken, newAdminId) => {
    console.log('🎯 AdminPanelWrapper: handleLogin called!', {newToken, newAdminId});
    setToken(newToken);
    setAdminId(newAdminId);
    setIsAuthenticated(true);
    console.log('✅ AdminPanelWrapper: Authentication state updated!');
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_id');
    setToken(null);
    setAdminId(null);
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <AdminLogin onLogin={handleLogin} />;
  }

  return (
    <AdminDashboard 
      token={token} 
      onLogout={handleLogout} 
    />
  );
};

export default AdminPanelWrapper;
