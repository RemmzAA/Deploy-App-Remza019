import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './AdminLicensePanel.css';

const AdminLicensePanel = () => {
  const [licenses, setLicenses] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);
  
  // Generate license form
  const [showGenerateForm, setShowGenerateForm] = useState(false);
  const [generateForm, setGenerateForm] = useState({
    userEmail: '',
    userName: '',
    licenseType: 'FULL'
  });

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  // Load licenses and stats
  useEffect(() => {
    loadLicenses();
    loadStats();
  }, []);

  const loadLicenses = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${backendUrl}/api/license/list`);
      const data = await response.json();
      
      if (data.success) {
        setLicenses(data.licenses);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error loading licenses:', error);
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/license/stats`);
      const data = await response.json();
      
      if (data.success) {
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleGenerateLicense = async () => {
    try {
      setMessage('Generating license key...');
      setIsError(false);
      
      const response = await fetch(`${backendUrl}/api/license/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(generateForm)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setMessage(`✅ License Generated: ${data.license_key}`);
        setIsError(false);
        setShowGenerateForm(false);
        setGenerateForm({ userEmail: '', userName: '', licenseType: 'FULL' });
        loadLicenses();
        loadStats();
      } else {
        setMessage(`❌ ${data.message}`);
        setIsError(true);
      }
    } catch (error) {
      setMessage(`❌ Error: ${error.message}`);
      setIsError(true);
    }
  };

  const handleDeactivateLicense = async (licenseKey) => {
    if (!window.confirm(`Are you sure you want to deactivate license: ${licenseKey}?`)) {
      return;
    }
    
    try {
      const response = await fetch(`${backendUrl}/api/license/deactivate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ license_key: licenseKey })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setMessage(`✅ License deactivated: ${licenseKey}`);
        setIsError(false);
        loadLicenses();
        loadStats();
      } else {
        setMessage(`❌ ${data.message}`);
        setIsError(true);
      }
    } catch (error) {
      setMessage(`❌ Error: ${error.message}`);
      setIsError(true);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setMessage(`✅ Copied to clipboard: ${text}`);
    setIsError(false);
    setTimeout(() => setMessage(''), 3000);
  };

  return (
    <div className="admin-license-panel">
      <div className="license-panel-header">
        <h2>🔑 License Management</h2>
        <button 
          className="btn-generate-license"
          onClick={() => setShowGenerateForm(!showGenerateForm)}
        >
          ➕ Generate New License
        </button>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="license-stats">
          <div className="stat-card">
            <span className="stat-value">{stats.total}</span>
            <span className="stat-label">Total Licenses</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{stats.active}</span>
            <span className="stat-label">Active</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{stats.full}</span>
            <span className="stat-label">Full Licenses</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{stats.trial}</span>
            <span className="stat-label">Trial Licenses</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{stats.activated}</span>
            <span className="stat-label">Activated</span>
          </div>
        </div>
      )}

      {/* Generate License Form */}
      {showGenerateForm && (
        <motion.div 
          className="generate-license-form"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h3>Generate New License</h3>
          <div className="form-group">
            <label>License Type</label>
            <select 
              value={generateForm.licenseType}
              onChange={(e) => setGenerateForm({...generateForm, licenseType: e.target.value})}
            >
              <option value="FULL">FULL</option>
              <option value="TRIAL">TRIAL</option>
            </select>
          </div>
          <div className="form-group">
            <label>User Email (Optional)</label>
            <input 
              type="email"
              value={generateForm.userEmail}
              onChange={(e) => setGenerateForm({...generateForm, userEmail: e.target.value})}
              placeholder="user@example.com"
            />
          </div>
          <div className="form-group">
            <label>User Name (Optional)</label>
            <input 
              type="text"
              value={generateForm.userName}
              onChange={(e) => setGenerateForm({...generateForm, userName: e.target.value})}
              placeholder="John Doe"
            />
          </div>
          <div className="form-actions">
            <button onClick={handleGenerateLicense} className="btn-primary">
              Generate
            </button>
            <button onClick={() => setShowGenerateForm(false)} className="btn-secondary">
              Cancel
            </button>
          </div>
        </motion.div>
      )}

      {/* Message */}
      {message && (
        <div className={`license-message ${isError ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      {/* License List */}
      <div className="license-list">
        <h3>All Licenses ({licenses.length})</h3>
        
        {loading ? (
          <div className="loading">Loading licenses...</div>
        ) : (
          <div className="license-table">
            <table>
              <thead>
                <tr>
                  <th>License Key</th>
                  <th>Type</th>
                  <th>User</th>
                  <th>Created</th>
                  <th>Activated</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {licenses.map(license => (
                  <tr key={license.license_key} className={!license.is_active ? 'inactive' : ''}>
                    <td>
                      <code className="license-key-display" onClick={() => copyToClipboard(license.license_key)}>
                        {license.license_key}
                      </code>
                    </td>
                    <td>
                      <span className={`badge badge-${license.license_type.toLowerCase()}`}>
                        {license.license_type}
                      </span>
                    </td>
                    <td>
                      {license.user_email || license.user_name || '-'}
                    </td>
                    <td>{new Date(license.created_at).toLocaleDateString()}</td>
                    <td>{license.activated_at ? new Date(license.activated_at).toLocaleDateString() : 'Not activated'}</td>
                    <td>
                      <span className={`status ${license.is_active ? 'active' : 'inactive'}`}>
                        {license.is_active ? '✅ Active' : '❌ Inactive'}
                      </span>
                    </td>
                    <td>
                      {license.is_active && (
                        <button 
                          onClick={() => handleDeactivateLicense(license.license_key)}
                          className="btn-deactivate"
                        >
                          Deactivate
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminLicensePanel;
