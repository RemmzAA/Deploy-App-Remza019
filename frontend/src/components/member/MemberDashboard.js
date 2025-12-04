import React, { useState, useEffect } from 'react';
import './MemberDashboard.css';

const MemberDashboard = () => {
  const [member, setMember] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('profile'); // 'profile', 'license', 'support'
  const [licenseKey, setLicenseKey] = useState('');
  const [supportTicket, setSupportTicket] = useState({
    subject: '',
    message: '',
    category: 'GENERAL',
    priority: 'NORMAL'
  });
  const [tickets, setTickets] = useState([]);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    loadMemberProfile();
    if (activeTab === 'support') {
      loadTickets();
    }
  }, [activeTab]);

  const loadMemberProfile = async () => {
    try {
      const token = localStorage.getItem('member_token');
      if (!token) {
        window.location.href = '/member/login';
        return;
      }

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/member/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (data.success) {
        setMember(data.member);
        localStorage.setItem('member_data', JSON.stringify(data.member));
      } else {
        handleLogout();
      }
    } catch (err) {
      console.error('Failed to load profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('member_token');
    localStorage.removeItem('member_data');
    window.location.href = '/';
  };

  const handleActivateLicense = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });

    try {
      const token = localStorage.getItem('member_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/member/activate-license`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ license_key: licenseKey })
      });

      const data = await response.json();

      if (data.success) {
        setMessage({ type: 'success', text: `License activated successfully! Type: ${data.license_type}` });
        setLicenseKey('');
        loadMemberProfile(); // Refresh profile
      } else {
        setMessage({ type: 'error', text: data.detail || 'License activation failed' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Network error. Please try again.' });
    }
  };

  const handleCreateTicket = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/support/create-ticket`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...supportTicket,
          member_email: member?.email
        })
      });

      const data = await response.json();

      if (data.success) {
        setMessage({ type: 'success', text: `Support ticket created! ID: ${data.ticket_id}` });
        setSupportTicket({ subject: '', message: '', category: 'GENERAL', priority: 'NORMAL' });
        loadTickets();
      } else {
        setMessage({ type: 'error', text: 'Failed to create ticket' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Network error. Please try again.' });
    }
  };

  const loadTickets = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/support/tickets?member_email=${member?.email}`
      );
      const data = await response.json();
      if (data.success) {
        setTickets(data.tickets);
      }
    } catch (err) {
      console.error('Failed to load tickets:', err);
    }
  };

  const getLicenseBadge = (type) => {
    const badges = {
      'TRIAL': { icon: '🧪', label: 'Trial', color: '#ffa500' },
      'BASIC': { icon: '🎖️', label: 'Basic', color: '#00bfff' },
      'PREMIUM': { icon: '🏆', label: 'Premium', color: '#ffd700' },
      'NONE': { icon: '❌', label: 'No License', color: '#888888' }
    };
    const badge = badges[type] || badges.NONE;
    return (
      <span className="license-badge" style={{ borderColor: badge.color, color: badge.color }}>
        {badge.icon} {badge.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="member-dashboard loading">
        <div className="loading-spinner">⏳</div>
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  if (!member) {
    return null;
  }

  return (
    <div className="member-dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <h1>🎮 Member Dashboard</h1>
          <div className="member-info">
            <span className="member-nickname">{member.nickname}</span>
            {getLicenseBadge(member.license_type)}
          </div>
        </div>
        <button className="logout-button" onClick={handleLogout}>
          🚪 Logout
        </button>
      </div>

      <div className="dashboard-tabs">
        <button
          className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          👤 Profile
        </button>
        <button
          className={`tab-button ${activeTab === 'license' ? 'active' : ''}`}
          onClick={() => setActiveTab('license')}
        >
          🔑 License
        </button>
        <button
          className={`tab-button ${activeTab === 'support' ? 'active' : ''}`}
          onClick={() => setActiveTab('support')}
        >
          💬 Support
        </button>
      </div>

      <div className="dashboard-content">
        {message.text && (
          <div className={`dashboard-message ${message.type}`}>
            {message.text}
          </div>
        )}

        {activeTab === 'profile' && (
          <div className="profile-tab">
            <div className="profile-card">
              <h2>👤 Profile Information</h2>
              <div className="profile-details">
                <div className="detail-row">
                  <span className="detail-label">Nickname:</span>
                  <span className="detail-value">{member.nickname}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Email:</span>
                  <span className="detail-value">{member.email}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Discord ID:</span>
                  <span className="detail-value">{member.discord_id}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Member ID:</span>
                  <span className="detail-value">{member.member_id}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Points:</span>
                  <span className="detail-value points">🎖️ {member.points || 0}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Level:</span>
                  <span className="detail-value level">⭐ {member.level || 1} - {member.level_name || 'Novice'}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'license' && (
          <div className="license-tab">
            <div className="license-card">
              <h2>🔑 License Management</h2>
              
              <div className="current-license">
                <h3>Current License Status</h3>
                <div className="license-status">
                  {getLicenseBadge(member.license_type)}
                  {member.license_expires_at && (
                    <p className="expiry-date">
                      Expires: {new Date(member.license_expires_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
              </div>

              <form onSubmit={handleActivateLicense} className="activate-form">
                <h3>Activate New License</h3>
                <div className="form-group">
                  <input
                    type="text"
                    value={licenseKey}
                    onChange={(e) => setLicenseKey(e.target.value.toUpperCase())}
                    placeholder="Enter license key (e.g., TRIAL-XXXXX-XXXXX-XXXXX)"
                    required
                  />
                </div>
                <button type="submit" className="activate-button">
                  ✅ Activate License
                </button>
              </form>

              <div className="license-info">
                <h3>📊 License Types</h3>
                <div className="license-types">
                  <div className="license-type-card">
                    <div className="type-icon">🧪</div>
                    <h4>TRIAL</h4>
                    <ul>
                      <li>Limited time access</li>
                      <li>Basic features</li>
                      <li>7-30 days duration</li>
                    </ul>
                  </div>
                  <div className="license-type-card">
                    <div className="type-icon">🎖️</div>
                    <h4>BASIC</h4>
                    <ul>
                      <li>Custom name & logo</li>
                      <li>Basic customization</li>
                      <li>Lifetime access</li>
                    </ul>
                  </div>
                  <div className="license-type-card premium">
                    <div className="type-icon">🏆</div>
                    <h4>PREMIUM</h4>
                    <ul>
                      <li>Full admin panel access</li>
                      <li>All features unlocked</li>
                      <li>Priority support</li>
                      <li>Lifetime updates</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'support' && (
          <div className="support-tab">
            <div className="support-card">
              <h2>💬 Support Center</h2>

              <form onSubmit={handleCreateTicket} className="support-form">
                <h3>Create New Ticket</h3>
                <div className="form-group">
                  <label>Category</label>
                  <select
                    value={supportTicket.category}
                    onChange={(e) => setSupportTicket({ ...supportTicket, category: e.target.value })}
                  >
                    <option value="GENERAL">General</option>
                    <option value="LICENSE">License Issue</option>
                    <option value="TECHNICAL">Technical Support</option>
                    <option value="BILLING">Billing</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Priority</label>
                  <select
                    value={supportTicket.priority}
                    onChange={(e) => setSupportTicket({ ...supportTicket, priority: e.target.value })}
                  >
                    <option value="LOW">Low</option>
                    <option value="NORMAL">Normal</option>
                    <option value="HIGH">High</option>
                    <option value="URGENT">Urgent</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Subject</label>
                  <input
                    type="text"
                    value={supportTicket.subject}
                    onChange={(e) => setSupportTicket({ ...supportTicket, subject: e.target.value })}
                    placeholder="Brief description of your issue"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Message</label>
                  <textarea
                    value={supportTicket.message}
                    onChange={(e) => setSupportTicket({ ...supportTicket, message: e.target.value })}
                    placeholder="Provide detailed information about your issue"
                    rows={5}
                    required
                  />
                </div>

                <button type="submit" className="submit-button">
                  📤 Submit Ticket
                </button>
              </form>

              <div className="tickets-list">
                <h3>Your Support Tickets</h3>
                {tickets.length === 0 ? (
                  <p className="no-tickets">No support tickets yet.</p>
                ) : (
                  <div className="tickets">
                    {tickets.map((ticket) => (
                      <div key={ticket.ticket_id} className="ticket-card">
                        <div className="ticket-header">
                          <span className="ticket-id">#{ticket.ticket_id}</span>
                          <span className={`ticket-status ${ticket.status.toLowerCase()}`}>
                            {ticket.status}
                          </span>
                        </div>
                        <h4>{ticket.subject}</h4>
                        <p className="ticket-category">{ticket.category} - {ticket.priority}</p>
                        <p className="ticket-date">
                          Created: {new Date(ticket.created_at).toLocaleString()}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MemberDashboard;
