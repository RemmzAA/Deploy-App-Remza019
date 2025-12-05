import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import './AnalyticsDashboard.css';

const AnalyticsDashboard = ({ user }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchAnalytics();
    }
  }, [user]);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/analytics/user/${user.id}`);
      setAnalytics(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="analytics-login-prompt">
        <h3>🔒 Login Required</h3>
        <p>Please login to view your analytics</p>
      </div>
    );
  }

  if (loading) {
    return <div className="analytics-loading">Loading analytics...</div>;
  }

  if (!analytics) {
    return <div className="analytics-error">Failed to load analytics</div>;
  }

  // Prepare chart data
  const chartData = {
    labels: Object.keys(analytics.daily_points_chart || {}),
    datasets: [{
      label: 'Points Earned',
      data: Object.values(analytics.daily_points_chart || {}),
      borderColor: '#00ff00',
      backgroundColor: 'rgba(0, 255, 0, 0.1)',
      tension: 0.4,
      fill: true
    }]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: '#464649'
        },
        ticks: {
          color: '#a9a9ac'
        }
      },
      x: {
        grid: {
          color: '#464649'
        },
        ticks: {
          color: '#a9a9ac'
        }
      }
    }
  };

  return (
    <div className="analytics-dashboard-container">
      <div className="analytics-header">
        <h2>📊 Your Analytics Dashboard</h2>
        <p>Track your progress and achievements</p>
      </div>

      {/* User Overview */}
      <div className="user-overview-card">
        <div className="overview-stat">
          <div className="stat-icon">👤</div>
          <div className="stat-content">
            <div className="stat-label">Username</div>
            <div className="stat-value">{analytics.user.username}</div>
          </div>
        </div>
        <div className="overview-stat">
          <div className="stat-icon">🏆</div>
          <div className="stat-content">
            <div className="stat-label">Level</div>
            <div className="stat-value">{analytics.user.level}</div>
          </div>
        </div>
        <div className="overview-stat">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <div className="stat-label">Total Points</div>
            <div className="stat-value">{analytics.user.total_points?.toLocaleString()}</div>
          </div>
        </div>
        <div className="overview-stat">
          <div className="stat-icon">📅</div>
          <div className="stat-content">
            <div className="stat-label">Member Since</div>
            <div className="stat-value">
              {new Date(analytics.user.member_since).toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="analytics-stats-grid">
        <div className="stat-card">
          <h3>Total Activities</h3>
          <div className="stat-big-value">{analytics.stats.total_activities}</div>
        </div>
        <div className="stat-card highlight">
          <h3>Points (Last 30 Days)</h3>
          <div className="stat-big-value">{analytics.stats.points_last_30_days}</div>
        </div>
        <div className="stat-card">
          <h3>Daily Average</h3>
          <div className="stat-big-value">{Math.round(analytics.stats.average_daily_points)}</div>
        </div>
      </div>

      {/* Points Chart */}
      <div className="chart-card">
        <h3>📈 Points Over Time (Last 30 Days)</h3>
        <div className="chart-wrapper">
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>

      {/* Activity Breakdown */}
      <div className="activity-breakdown-card">
        <h3>🎯 Activity Breakdown</h3>
        <div className="activity-grid">
          {Object.entries(analytics.activity_breakdown || {}).map(([activity, count]) => (
            <div key={activity} className="activity-item">
              <span className="activity-name">{activity.replace('_', ' ')}</span>
              <span className="activity-count">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activities */}
      <div className="recent-activities-card">
        <h3>🕒 Recent Activities</h3>
        <div className="activities-list">
          {analytics.recent_activities?.slice(0, 10).map((activity, index) => (
            <div key={index} className="activity-log-item">
              <span className="activity-type">{activity.activity_type}</span>
              <span className="activity-points">+{activity.points} pts</span>
              <span className="activity-time">
                {new Date(activity.timestamp).toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Badges */}
      {analytics.user.badges?.length > 0 && (
        <div className="badges-card">
          <h3>🏅 Your Badges</h3>
          <div className="badges-grid">
            {analytics.user.badges.map((badge, index) => (
              <div key={index} className="badge-item">
                <span className="badge-icon">🏅</span>
                <span className="badge-name">{badge}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;
