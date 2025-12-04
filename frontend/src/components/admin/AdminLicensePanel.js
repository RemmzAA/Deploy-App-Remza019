import React, { useState, useEffect } from 'react';
import './AdminLicensePanel.css';

const AdminLicensePanel = ({ token }) => {
  const [licenses, setLicenses] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [newLicense, setNewLicense] = useState({
    license_type: 'TRIAL',
    duration_days: 7,
    user_email: '',
    user_name: ''
  });

  useEffect(() => {
    loadLicenses();
    loadStats();
  }, []);

  const loadLicenses = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/license/list`
      );
      const data = await response.json();
      if (data.success) {
        setLicenses(data.licenses);
      }
    } catch (err) {
      console.error('Failed to load licenses:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/license/stats`
      );
      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
      }
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleGenerateLicense = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/license/generate`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newLicense)
        }
      );

      const data = await response.json();

      if (data.success) {
        setMessage({
          type: 'success',
          text: `License generated! Key: ${data.license_key}`
        });
        setNewLicense({
          license_type: 'TRIAL',
          duration_days: 7,
          user_email: '',
          user_name: ''
        });
        loadLicenses();
        loadStats();
      } else {
        setMessage({ type: 'error', text: 'Failed to generate license' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Network error' });
    }
  };

  const handleDeactivateLicense = async (licenseKey) => {
    if (!window.confirm('Are you sure you want to deactivate this license?')) {
      return;
    }

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/license/deactivate`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ license_key: licenseKey })
        }
      );

      const data = await response.json();

      if (data.success) {
        setMessage({ type: 'success', text: 'License deactivated' });
        loadLicenses();
        loadStats();
      } else {
        setMessage({ type: 'error', text: 'Failed to deactivate' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Network error' });
    }
  };

  const getLicenseTypeBadge = (type) => {
    const colors = {
      TRIAL: '#ffa500',
      BASIC: '#00bfff',
      PREMIUM: '#ffd700'
    };
    return (
      <span
        className="license-type-badge"
        style={{ background: colors[type] || '#888' }}
      >
        {type}
      </span>
    );
  };

  if (loading) {
    return <div className="admin-license-loading">Loading licenses...</div>;
  }

  return (
    <div className="admin-license-panel">
      <h2>🔑 License Management</h2>

      {message.text && (
        <div className={`admin-message ${message.type}`}>{message.text}</div>
      )}

      {stats && (
        <div className="license-stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Licenses</div>
          </div>
          <div className="stat-card active">
            <div className="stat-icon">✅</div>
            <div className="stat-value">{stats.active}</div>
            <div className="stat-label">Active</div>
          </div>
          <div className="stat-card trial">
            <div className="stat-icon">🧪</div>
            <div className="stat-value">{stats.trial}</div>
            <div className="stat-label">Trial</div>
          </div>
          <div className="stat-card basic">
            <div className="stat-icon">🎖️</div>
            <div className="stat-value">{stats.basic}</div>
            <div className="stat-label">Basic</div>
          </div>
          <div className="stat-card premium">
            <div className="stat-icon">🏆</div>
            <div className="stat-value">{stats.premium}</div>
            <div className="stat-label">Premium</div>
          </div>
          <div className="stat-card assigned">
            <div className="stat-icon">👥</div>
            <div className="stat-value">{stats.assigned_to_members}</div>
            <div className="stat-label">Assigned</div>
          </div>
        </div>
      )}

      <div className="generate-license-section">
        <h3>🎫 Generate New License</h3>
        <form onSubmit={handleGenerateLicense} className="generate-form">
          <div className="form-row">
            <div className="form-group">
              <label>License Type</label>
              <select
                value={newLicense.license_type}
                onChange={(e) =>
                  setNewLicense({ ...newLicense, license_type: e.target.value })
                }
              >
                <option value="TRIAL">Trial</option>
                <option value="BASIC">Basic</option>
                <option value="PREMIUM">Premium</option>
              </select>
            </div>

            {newLicense.license_type === 'TRIAL' && (
              <div className="form-group">
                <label>Duration (days)</label>
                <input
                  type="number"
                  value={newLicense.duration_days}
                  onChange={(e) =>
                    setNewLicense({
                      ...newLicense,
                      duration_days: parseInt(e.target.value)
                    })
                  }
                  min="1"
                  max="365"
                />
              </div>
            )}

            <div className="form-group">
              <label>Email (optional)</label>
              <input
                type="email"
                value={newLicense.user_email}
                onChange={(e) =>
                  setNewLicense({ ...newLicense, user_email: e.target.value })
                }
                placeholder="customer@email.com"
              />
            </div>

            <div className="form-group">
              <label>Name (optional)</label>
              <input
                type="text"
                value={newLicense.user_name}
                onChange={(e) =>
                  setNewLicense({ ...newLicense, user_name: e.target.value })
                }
                placeholder="Customer Name"
              />
            </div>
          </div>

          <button type="submit" className="generate-button">
            ✨ Generate License
          </button>
        </form>
      </div>

      <div className="licenses-table-section">
        <h3>📊 All Licenses ({licenses.length})</h3>
        <div className="licenses-table">
          <table>
            <thead>
              <tr>
                <th>License Key</th>
                <th>Type</th>
                <th>Status</th>
                <th>Assigned To</th>
                <th>Created</th>
                <th>Expires</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {licenses.map((license) => (
                <tr key={license.license_key}>
                  <td className="license-key-cell">
                    <code>{license.license_key}</code>
                  </td>
                  <td>{getLicenseTypeBadge(license.license_type)}</td>
                  <td>
                    <span
                      className={`status-badge ${
                        license.is_active ? 'active' : 'inactive'
                      }`}
                    >
                      {license.is_active ? '✅ Active' : '❌ Inactive'}
                    </span>
                  </td>
                  <td>
                    {license.assigned_nickname ? (
                      <div className="assigned-info">
                        <div>{license.assigned_nickname}</div>
                        <div className="email-small">
                          {license.assigned_email}
                        </div>
                      </div>
                    ) : (
                      <span className="unassigned">Not assigned</span>
                    )}
                  </td>
                  <td>{new Date(license.created_at).toLocaleDateString()}</td>
                  <td>
                    {license.expires_at
                      ? new Date(license.expires_at).toLocaleDateString()
                      : 'Never'}
                  </td>
                  <td>
                    {license.is_active && (
                      <button
                        className="deactivate-button"
                        onClick={() =>
                          handleDeactivateLicense(license.license_key)
                        }
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
      </div>
    </div>
  );
};

export default AdminLicensePanel;
