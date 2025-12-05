import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ReferralDashboard.css';

const ReferralDashboard = ({ user }) => {
  const [referralData, setReferralData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (user) {
      fetchReferralStats();
    }
  }, [user]);

  const fetchReferralStats = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/referrals/stats/${user.id}`);
      setReferralData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching referral stats:', error);
      setLoading(false);
    }
  };

  const generateCode = async () => {
    try {
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/referrals/generate`, {
        user_id: user.id,
        username: user.username
      });
      if (response.data.success) {
        fetchReferralStats();
      }
    } catch (error) {
      console.error('Error generating referral code:', error);
    }
  };

  const copyReferralLink = () => {
    const link = `${window.location.origin}/join?ref=${referralData.referral_code}`;
    navigator.clipboard.writeText(link);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!user) {
    return (
      <div className="referral-login-prompt">
        <h3>🔒 Login Required</h3>
        <p>Please login to access your referral dashboard</p>
      </div>
    );
  }

  if (loading) {
    return <div className="referral-loading">Loading referral dashboard...</div>;
  }

  if (!referralData?.has_referral_code) {
    return (
      <div className="referral-generate-container">
        <h2>🤝 Referral Program</h2>
        <p>Invite friends and earn rewards!</p>
        <button onClick={generateCode} className="generate-code-btn">
          Generate My Referral Code
        </button>
      </div>
    );
  }

  return (
    <div className="referral-dashboard-container">
      <div className="referral-header">
        <h2>🤝 Your Referral Dashboard</h2>
        <p>Share your link and earn rewards!</p>
      </div>

      {/* Referral Link Card */}
      <div className="referral-link-card">
        <h3>Your Referral Link</h3>
        <div className="link-display">
          <input 
            type="text" 
            value={`${window.location.origin}${referralData.referral_link}`}
            readOnly
          />
          <button onClick={copyReferralLink} className="copy-btn">
            {copied ? '✓ Copied!' : '📋 Copy'}
          </button>
        </div>
        <div className="referral-code-display">
          <span>Referral Code:</span>
          <code>{referralData.referral_code}</code>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="referral-stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-value">{referralData.total_referrals}</div>
          <div className="stat-label">Total Referrals</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-value">{referralData.total_points_earned}</div>
          <div className="stat-label">Points Earned</div>
        </div>

        <div className="stat-card highlight">
          <div className="stat-icon">🏆</div>
          <div className="stat-value">{referralData.milestones_achieved?.length || 0}</div>
          <div className="stat-label">Milestones Achieved</div>
        </div>
      </div>

      {/* Next Milestone */}
      {referralData.next_milestone && (
        <div className="next-milestone-card">
          <h3>🎯 Next Milestone</h3>
          <div className="milestone-info">
            <p>Refer <strong>{referralData.next_milestone.remaining}</strong> more friends to unlock:</p>
            <div className="milestone-reward">
              <span className="reward-badge">{referralData.next_milestone.reward.badge}</span>
              <span className="reward-points">⭐ {referralData.next_milestone.reward.points} points</span>
            </div>
          </div>
          <div className="milestone-progress">
            <div 
              className="progress-bar"
              style={{ 
                width: `${(referralData.total_referrals / referralData.next_milestone.count) * 100}%` 
              }}
            />
          </div>
        </div>
      )}

      {/* Recent Referrals */}
      {referralData.recent_referrals?.length > 0 && (
        <div className="recent-referrals-card">
          <h3>🕒 Recent Referrals</h3>
          <div className="referrals-list">
            {referralData.recent_referrals.slice(0, 10).map((ref, index) => (
              <div key={index} className="referral-item">
                <span className="referral-username">{ref.referred_username}</span>
                <span className="referral-date">
                  {new Date(ref.created_at).toLocaleDateString()}
                </span>
                <span className="referral-points">+{ref.rewards_given.referrer} pts</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rewards Info */}
      <div className="rewards-info-card">
        <h3>🎁 Referral Rewards</h3>
        <ul>
          <li><strong>50 points</strong> when friend signs up</li>
          <li><strong>100 points</strong> when friend completes first activity</li>
          <li><strong>500 points</strong> when friend subscribes</li>
          <li><strong>Milestone bonuses</strong> at 10, 25, 50, 100 referrals!</li>
        </ul>
      </div>
    </div>
  );
};

export default ReferralDashboard;