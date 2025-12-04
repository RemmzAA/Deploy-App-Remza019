import React, { useState, useEffect } from 'react';
import './AdminMemberPanel.css';

const AdminMemberPanel = ({ token }) => {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    verified: 0,
    active: 0,
    withLicense: 0
  });

  useEffect(() => {
    loadMembers();
  }, []);

  const loadMembers = async () => {
    try {
      // Note: This endpoint doesn't exist yet, but we'll use direct DB query or create it
      // For now, we'll show a placeholder
      setLoading(false);
      // TODO: Implement member list endpoint
    } catch (err) {
      console.error('Failed to load members:', err);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="admin-member-loading">Loading members...</div>;
  }

  return (
    <div className="admin-member-panel">
      <h2>👥 Member Management</h2>

      <div className="member-stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Members</div>
        </div>
        <div className="stat-card verified">
          <div className="stat-icon">✅</div>
          <div className="stat-value">{stats.verified}</div>
          <div className="stat-label">Email Verified</div>
        </div>
        <div className="stat-card active">
          <div className="stat-icon">🟢</div>
          <div className="stat-value">{stats.active}</div>
          <div className="stat-label">Active Members</div>
        </div>
        <div className="stat-card licensed">
          <div className="stat-icon">🔑</div>
          <div className="stat-value">{stats.withLicense}</div>
          <div className="stat-label">With License</div>
        </div>
      </div>

      <div className="members-section">
        <h3>📊 Member List</h3>
        <div className="info-message">
          <p>ℹ️ Member management coming soon!</p>
          <p>Members can register at <strong>/member/login</strong></p>
          <p>View their dashboard at <strong>/member/dashboard</strong></p>
        </div>
      </div>
    </div>
  );
};

export default AdminMemberPanel;
