import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../i18n/LanguageContext';
import './AdminLogin.css';

const AdminLogin = ({ onLogin }) => {
  const { t } = useLanguage();
  const { login } = useAuth();
  const navigate = useNavigate();
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      console.log('🔐 Attempting admin login...');
      const result = await login(credentials.username, credentials.password);

      if (result.success) {
        console.log('✅ Login successful!');
        
        // Call parent callback if provided (for backwards compatibility)
        if (onLogin) {
          onLogin(result.token, result.admin_id);
        }
        
        console.log('✅ Admin authentication complete!');
      } else {
        console.error('❌ Login failed:', result.message);
        setError(result.message || 'Login failed');
      }
    } catch (error) {
      console.error('❌ Login error:', error);
      setError(`Network error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="admin-login-container">
      {/* Matrix Rain Background */}
      <div className="matrix-background">
        <canvas id="matrix-canvas"></canvas>
      </div>

      <motion.div 
        className="login-form-container"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
      >
        <div className="login-header">
          <motion.h1
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            REMZA019 GAMING
          </motion.h1>
          <motion.h2
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {t('adminLogin')}
          </motion.h2>
        </div>

        <motion.form 
          className="login-form"
          onSubmit={handleSubmit}
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <div className="input-group">
            <label htmlFor="username">{t('username')}</label>
            <input
              type="text"
              id="username"
              name="username"
              value={credentials.username}
              onChange={handleInputChange}
              required
              placeholder={t('username')}
              disabled={loading}
            />
          </div>

          <div className="input-group">
            <label htmlFor="password">{t('password')}</label>
            <input
              type="password"
              id="password"
              name="password"
              value={credentials.password}
              onChange={handleInputChange}
              required
              placeholder={t('password')}
              disabled={loading}
            />
          </div>

          {error && (
            <motion.div 
              className="error-message"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              ❌ {error}
            </motion.div>
          )}

          <motion.button
            type="submit"
            className="login-button matrix-button"
            disabled={loading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                {t('processing')}
              </>
            ) : (
              <>
                🎮 {t('login')}
              </>
            )}
          </motion.button>
        </motion.form>

        <div className="login-footer">
          <p>🔐 Authorized access only</p>
          <p>Default: admin / remza019admin</p>
        </div>
      </motion.div>
    </div>
  );
};

export default AdminLogin;