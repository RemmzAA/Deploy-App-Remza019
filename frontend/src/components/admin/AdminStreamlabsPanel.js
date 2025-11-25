import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './AdminStreamlabsPanel.css';

const AdminStreamlabsPanel = ({ token }) => {
  const [donations, setDonations] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mockMode, setMockMode] = useState(true);

  const API_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchDonations();
    fetchAlerts();
    fetchStats();
  }, []);

  const fetchDonations = async () => {
    try {
      const response = await fetch(`${API_URL}/api/streamlabs/donations`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setDonations(data.donations || []);
        setMockMode(data.mock_mode || false);
      }
    } catch (error) {
      console.error('Failed to fetch donations:', error);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await fetch(`${API_URL}/api/streamlabs/alerts`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts || []);
      }
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/streamlabs/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const testAlert = async (alertType) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/streamlabs/test-alert`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ alert_type: alertType })
      });
      if (response.ok) {
        alert('✅ Test alert triggered!');
      }
    } catch (error) {
      alert('❌ Failed to trigger test alert');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount, currency = 'USD') => {
    return new Intl.NumberFormat('sr-Latn-RS', {
      style: 'currency',
      currency: currency
    }).format(amount);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('sr-Latn-RS', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="streamlabs-panel">
      <motion.h2
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        💰 Streamlabs Integration
      </motion.h2>

      {mockMode && (
        <div className="mock-warning">
          ⚠️ MOCK MODE - Connect Streamlabs account for live data
        </div>
      )}

      {/* Stats Overview */}
      {stats && (
        <motion.div
          className="stats-overview"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="stat-card">
            <div className="stat-icon">💵</div>
            <div className="stat-content">
              <div className="stat-value">{formatCurrency(stats.total_donations || 0)}</div>
              <div className="stat-label">Total Donations</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-value">{stats.donation_count || 0}</div>
              <div className="stat-label">Donation Count</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🎯</div>
            <div className="stat-content">
              <div className="stat-value">{formatCurrency(stats.average_donation || 0)}</div>
              <div className="stat-label">Average</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">👑</div>
            <div className="stat-content">
              <div className="stat-value">{formatCurrency(stats.top_donation || 0)}</div>
              <div className="stat-label">Top Donation</div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Recent Donations */}
      <motion.div
        className="donations-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="section-header">
          <h3>📜 Recent Donations</h3>
          <button
            className="refresh-btn"
            onClick={fetchDonations}
            disabled={loading}
          >
            🔄 Refresh
          </button>
        </div>

        <div className="donations-list">
          {donations.length > 0 ? (
            donations.map((donation, index) => (
              <motion.div
                key={donation.id}
                className="donation-card"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <div className="donation-amount">
                  {formatCurrency(donation.amount, donation.currency)}
                </div>
                <div className="donation-info">
                  <div className="donation-name">{donation.name}</div>
                  {donation.message && (
                    <div className="donation-message">
                      💬 "{donation.message}"
                    </div>
                  )}
                  <div className="donation-time">
                    {formatDate(donation.created_at)}
                  </div>
                </div>
              </motion.div>
            ))
          ) : (
            <div className="no-data">No donations yet</div>
          )}
        </div>
      </motion.div>

      {/* Alert Testing */}
      <motion.div
        className="alerts-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h3>🔔 Test Alerts</h3>
        <div className="alert-buttons">
          <button
            className="alert-test-btn donation-alert"
            onClick={() => testAlert('donation')}
            disabled={loading}
          >
            💰 Test Donation Alert
          </button>
          <button
            className="alert-test-btn follow-alert"
            onClick={() => testAlert('follow')}
            disabled={loading}
          >
            👤 Test Follow Alert
          </button>
          <button
            className="alert-test-btn sub-alert"
            onClick={() => testAlert('subscription')}
            disabled={loading}
          >
            ⭐ Test Subscription Alert
          </button>
        </div>
      </motion.div>

      {/* Setup Instructions */}
      <div className="setup-section">
        <h3>⚙️ Setup Instructions</h3>
        <div className="setup-steps">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-content">
              <strong>Get Streamlabs Token</strong>
              <p>Visit: <a href="https://streamlabs.com/dashboard#/settings/api-settings" target="_blank" rel="noopener noreferrer">Streamlabs API Settings</a></p>
              <p>Generate Socket API Token</p>
            </div>
          </div>

          <div className="step">
            <div className="step-number">2</div>
            <div className="step-content">
              <strong>Configure Backend</strong>
              <p>Add to <code>/app/backend/.env</code>:</p>
              <pre>STREAMLABS_CLIENT_ID=your_client_id
STREAMLABS_CLIENT_SECRET=your_client_secret
STREAMLABS_ACCESS_TOKEN=your_access_token</pre>
            </div>
          </div>

          <div className="step">
            <div className="step-number">3</div>
            <div className="step-content">
              <strong>Restart Backend</strong>
              <p>Restart backend service to apply changes</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminStreamlabsPanel;
