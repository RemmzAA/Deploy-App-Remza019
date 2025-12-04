import React, { useState, useEffect } from 'react';
import './AdminMemberPanel.css';

const AdminMemberPanel = ({ token }) => {
  const [activeView, setActiveView] = useState('pending'); // 'pending' or 'all'
  const [members, setMembers] = useState([]);
  const [pendingMembers, setPendingMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [stats, setStats] = useState({
    total: 0,
    verified: 0,
    pending: 0,
    active: 0,
    banned: 0,
    with_license: 0
  });

  useEffect(() => {
    loadStats();
    loadPendingMembers();
    loadAllMembers();
  }, []);

  const loadStats = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/member/admin/member-stats`
      );
      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
      }
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const loadPendingMembers = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/member/admin/pending-members`
      );
      const data = await response.json();
      if (data.success) {
        setPendingMembers(data.members);
      }
    } catch (err) {
      console.error('Failed to load pending members:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadAllMembers = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/member/admin/all-members`
      );
      const data = await response.json();
      if (data.success) {
        setMembers(data.members);
      }
    } catch (err) {
      console.error('Failed to load all members:', err);
    }
  };

  const handleVerifyMember = async (memberId, nickname) => {
    if (!window.confirm(`Verify member: ${nickname}?`)) return;

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/member/admin/verify-member?member_id=${memberId}`,
        { method: 'POST' }
      );
      const data = await response.json();

      if (data.success) {
        setMessage({ type: 'success', text: `✅ ${nickname} verified!` });
        loadStats();
        loadPendingMembers();
        loadAllMembers();
      } else {
        setMessage({ type: 'error', text: 'Verification failed' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Network error' });
    }
  };

  const handleBanMember = async (memberId, nickname) => {
    const reason = window.prompt(`Ban reason for ${nickname}:`, 'Violation of terms');
    if (!reason) return;

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/member/admin/ban-member?member_id=${memberId}&reason=${encodeURIComponent(reason)}`,
        { method: 'POST' }
      );
      const data = await response.json();

      if (data.success) {
        setMessage({ type: 'success', text: `🚫 ${nickname} banned` });
        loadStats();
        loadAllMembers();
      } else {
        setMessage({ type: 'error', text: 'Ban failed' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Network error' });
    }
  };

  const handleUnbanMember = async (memberId, nickname) => {
    if (!window.confirm(`Unban member: ${nickname}?`)) return;

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/member/admin/unban-member?member_id=${memberId}`,
        { method: 'POST' }
      );
      const data = await response.json();

      if (data.success) {
        setMessage({ type: 'success', text: `✅ ${nickname} unbanned` });
        loadStats();
        loadAllMembers();
      } else {
        setMessage({ type: 'error', text: 'Unban failed' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Network error' });
    }
  };

  if (loading) {
    return <div className="admin-member-loading">⏳ Loading members...</div>;
  }

  return (
    <div className="admin-member-panel">
      <h2>👥 Member Management</h2>

      {message.text && (
        <div className={`admin-message ${message.type}`}>{message.text}</div>
      )}

      <div className="member-stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Members</div>
        </div>
        <div className="stat-card pending">
          <div className="stat-icon">⏳</div>
          <div className="stat-value">{stats.pending}</div>
          <div className="stat-label">Pending Verification</div>
        </div>
        <div className="stat-card verified">
          <div className="stat-icon">✅</div>
          <div className="stat-value">{stats.verified}</div>
          <div className="stat-label">Verified</div>
        </div>
        <div className="stat-card active">
          <div className="stat-icon">🟢</div>
          <div className="stat-value">{stats.active}</div>
          <div className="stat-label">Active</div>
        </div>
        <div className="stat-card banned">
          <div className="stat-icon">🚫</div>
          <div className="stat-value">{stats.banned}</div>
          <div className="stat-label">Banned</div>
        </div>
        <div className="stat-card licensed">
          <div className="stat-icon">🔑</div>
          <div className="stat-value">{stats.with_license}</div>
          <div className="stat-label">With License</div>
        </div>
      </div>

      <div className="view-tabs">
        <button
          className={`view-tab ${activeView === 'pending' ? 'active' : ''}`}
          onClick={() => setActiveView('pending')}
        >
          ⏳ Pending Verification ({pendingMembers.length})
        </button>
        <button
          className={`view-tab ${activeView === 'all' ? 'active' : ''}`}
          onClick={() => setActiveView('all')}
        >
          📋 All Members ({members.length})
        </button>
      </div>

      {activeView === 'pending' && (
        <div className="members-section">
          <h3>⏳ Pending Verification</h3>
          {pendingMembers.length === 0 ? (
            <div className="info-message">
              <p>✅ No pending verifications!</p>
            </div>
          ) : (
            <div className="members-table">
              <table>
                <thead>
                  <tr>
                    <th>Nickname</th>
                    <th>Email</th>
                    <th>Discord ID</th>
                    <th>Member ID</th>
                    <th>Registered</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {pendingMembers.map((member) => (
                    <tr key={member.member_id}>
                      <td className="nickname-cell">{member.nickname}</td>
                      <td>{member.email}</td>
                      <td>{member.discord_id}</td>
                      <td><code>{member.member_id}</code></td>
                      <td>{new Date(member.created_at).toLocaleDateString()}</td>
                      <td>
                        <button
                          className="verify-button"
                          onClick={() => handleVerifyMember(member.member_id, member.nickname)}
                        >
                          ✅ Verify
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeView === 'all' && (
        <div className="members-section">
          <h3>📋 All Members</h3>
          <div className="members-table">
            <table>
              <thead>
                <tr>
                  <th>Nickname</th>
                  <th>Email</th>
                  <th>Discord ID</th>
                  <th>Status</th>
                  <th>License</th>
                  <th>Points</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {members.map((member) => (
                  <tr key={member.member_id}>
                    <td className="nickname-cell">{member.nickname}</td>
                    <td>{member.email}</td>
                    <td>{member.discord_id}</td>
                    <td>
                      {!member.email_verified ? (
                        <span className="status-badge pending">⏳ Pending</span>
                      ) : member.is_banned ? (
                        <span className="status-badge banned">🚫 Banned</span>
                      ) : (
                        <span className="status-badge active">✅ Active</span>
                      )}
                    </td>
                    <td>
                      <span className={`license-badge ${member.license_type.toLowerCase()}`}>
                        {member.license_type}
                      </span>
                    </td>
                    <td>{member.points || 0}</td>
                    <td>
                      {!member.email_verified ? (
                        <button
                          className="verify-button"
                          onClick={() => handleVerifyMember(member.member_id, member.nickname)}
                        >
                          Verify
                        </button>
                      ) : member.is_banned ? (
                        <button
                          className="unban-button"
                          onClick={() => handleUnbanMember(member.member_id, member.nickname)}
                        >
                          Unban
                        </button>
                      ) : (
                        <button
                          className="ban-button"
                          onClick={() => handleBanMember(member.member_id, member.nickname)}
                        >
                          Ban
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminMemberPanel;
