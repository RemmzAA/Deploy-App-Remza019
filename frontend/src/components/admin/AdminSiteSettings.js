import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import './AdminSiteSettings.css';

const AdminSiteSettings = () => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  
  const [settings, setSettings] = useState({
    distributionMode: false,
    enablePWAInstall: true,
    aboutSectionTitle: '',
    pwaInstallTitle: '',
    adminPanelTitle: '',
    copyrightText: '',
    tagline: ''
  });

  // Load current settings
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/customization/current`);
      const data = await response.json();
      
      if (data.success && data.data) {
        setSettings({
          distributionMode: data.data.distributionMode || false,
          enablePWAInstall: data.data.enablePWAInstall !== false,
          aboutSectionTitle: data.data.aboutSectionTitle || '',
          pwaInstallTitle: data.data.pwaInstallTitle || '',
          adminPanelTitle: data.data.adminPanelTitle || '',
          copyrightText: data.data.copyrightText || '',
          tagline: data.data.tagline || ''
        });
      }
      setLoading(false);
    } catch (error) {
      console.error('Failed to load settings:', error);
      setLoading(false);
    }
  };

  const showMessage = (text, type = 'success') => {
    setMessage(text);
    setMessageType(type);
    setTimeout(() => {
      setMessage('');
      setMessageType('');
    }, 3000);
  };

  const handleToggle = async (field) => {
    const newValue = !settings[field];
    
    try {
      // Get current customization
      const currentResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/customization/current`);
      const currentData = await currentResponse.json();
      
      if (!currentData.success) {
        showMessage('Failed to load current settings', 'error');
        return;
      }

      // Update with new value
      const updatedData = {
        ...currentData.data,
        [field]: newValue
      };

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/customization/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updatedData)
      });

      const result = await response.json();

      if (result.success) {
        setSettings(prev => ({ ...prev, [field]: newValue }));
        showMessage(`${field} updated successfully!`, 'success');
        
        // Reload page after 1 second to apply changes
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      } else {
        showMessage(result.message || 'Update failed', 'error');
      }
    } catch (error) {
      console.error('Toggle error:', error);
      showMessage('Network error. Please try again.', 'error');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSettings(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    try {
      // Get current customization
      const currentResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/customization/current`);
      const currentData = await currentResponse.json();
      
      if (!currentData.success) {
        showMessage('Failed to load current settings', 'error');
        return;
      }

      // Update with new values
      const updatedData = {
        ...currentData.data,
        ...settings
      };

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/customization/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updatedData)
      });

      const result = await response.json();

      if (result.success) {
        showMessage('Settings saved successfully!', 'success');
      } else {
        showMessage(result.message || 'Save failed', 'error');
      }
    } catch (error) {
      console.error('Save error:', error);
      showMessage('Network error. Please try again.', 'error');
    }
  };

  if (loading) {
    return <div className="admin-site-settings loading">Loading settings...</div>;
  }

  return (
    <div className="admin-site-settings">
      <h2>⚙️ Site Settings</h2>

      {/* Message Display */}
      {message && (
        <motion.div
          className={`message ${messageType}`}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {message}
        </motion.div>
      )}

      {/* Distribution Mode */}
      <div className="setting-section highlight">
        <div className="setting-header">
          <div>
            <h3>🚀 Distribution Mode</h3>
            <p className="setting-description">
              Hide admin button and developer features from main page. 
              Perfect for distributing your app to end-users.
            </p>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={settings.distributionMode}
              onChange={() => handleToggle('distributionMode')}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        {settings.distributionMode && (
          <div className="setting-info success">
            ✅ Distribution mode is ACTIVE. Users won't see admin access button.
          </div>
        )}
      </div>

      {/* PWA Install */}
      <div className="setting-section">
        <div className="setting-header">
          <div>
            <h3>📱 PWA Install Button</h3>
            <p className="setting-description">
              Allow users to install your app as a Progressive Web App.
            </p>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={settings.enablePWAInstall}
              onChange={() => handleToggle('enablePWAInstall')}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
      </div>

      {/* Text Customization */}
      <div className="setting-section">
        <h3>✏️ Text Customization</h3>
        
        <div className="form-group">
          <label>About Section Title</label>
          <input
            type="text"
            name="aboutSectionTitle"
            value={settings.aboutSectionTitle}
            onChange={handleInputChange}
            placeholder="About 019 Solutions"
          />
        </div>

        <div className="form-group">
          <label>PWA Install Title</label>
          <input
            type="text"
            name="pwaInstallTitle"
            value={settings.pwaInstallTitle}
            onChange={handleInputChange}
            placeholder="📱 Install 019 Solutions App"
          />
        </div>

        <div className="form-group">
          <label>Admin Panel Title</label>
          <input
            type="text"
            name="adminPanelTitle"
            value={settings.adminPanelTitle}
            onChange={handleInputChange}
            placeholder="🎮 REMZA019 Admin Panel"
          />
        </div>

        <div className="form-group">
          <label>Copyright Text</label>
          <input
            type="text"
            name="copyrightText"
            value={settings.copyrightText}
            onChange={handleInputChange}
            placeholder="© 2025 019 Solutions. All rights reserved."
          />
        </div>

        <div className="form-group">
          <label>Tagline</label>
          <input
            type="text"
            name="tagline"
            value={settings.tagline}
            onChange={handleInputChange}
            placeholder="🎮 Professional Gaming Content Creator"
          />
        </div>

        <button className="save-btn" onClick={handleSave}>
          💾 Save Text Settings
        </button>
      </div>

      {/* Distribution Instructions */}
      <div className="setting-section info-section">
        <h3>📦 Distribution Guide</h3>
        <div className="distribution-steps">
          <div className="step">
            <span className="step-number">1</span>
            <div>
              <h4>Enable Distribution Mode</h4>
              <p>Toggle "Distribution Mode" to hide admin access</p>
            </div>
          </div>
          <div className="step">
            <span className="step-number">2</span>
            <div>
              <h4>Customize Your Brand</h4>
              <p>Set site name, logo, colors in Customization tab</p>
            </div>
          </div>
          <div className="step">
            <span className="step-number">3</span>
            <div>
              <h4>Deploy to Production</h4>
              <p>Build and deploy your customized gaming platform</p>
            </div>
          </div>
        </div>
        <p className="note">
          💡 <strong>Note:</strong> Admin panel will still be accessible at <code>/admin</code> URL 
          even in distribution mode. Only the visible button is hidden.
        </p>
      </div>
    </div>
  );
};

export default AdminSiteSettings;
