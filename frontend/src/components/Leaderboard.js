import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './Leaderboard.css';

const Leaderboard = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchLeaderboard();
    fetchStats();
    
    // Refresh every 30 seconds
    const interval = setInterval(() => {
      fetchLeaderboard();
      fetchStats();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchLeaderboard = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/leaderboard/top?limit=10`);
      const data = await response.json();
      setLeaderboard(data.leaderboard || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/leaderboard/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  if (loading) {
    return (
      <div className="leaderboard-loading">
        <div className="spinner"></div>
        <p>Loading leaderboard...</p>
      </div>
    );
  }

  return (
    <motion.section 
      className="leaderboard-section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
    >
      <div className="leaderboard-container">
        <motion.h2 
          className="leaderboard-title"
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          🏆 TOP VIEWERS LEADERBOARD
        </motion.h2>

        {stats && (
          <div className="leaderboard-stats">
            <div className="stat-card">
              <span className="stat-value">{stats.total_viewers || 0}</span>
              <span className="stat-label">Total Viewers</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{(stats.total_points || 0).toLocaleString()}</span>
              <span className="stat-label">Points Distributed</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{stats.average_points || 0}</span>
              <span className="stat-label">Avg Points</span>
            </div>
          </div>
        )}

        <div className="leaderboard-list">
          {leaderboard.length === 0 ? (
            <div className="no-data">
              <p>🎮 No viewers yet. Be the first to join!</p>
            </div>
          ) : (
            leaderboard.map((entry, index) => (
              <motion.div
                key={entry.user_id}
                className={`leaderboard-entry rank-${entry.rank}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="entry-rank">
                  {entry.rank === 1 && '🥇'}
                  {entry.rank === 2 && '🥈'}
                  {entry.rank === 3 && '🥉'}
                  {entry.rank > 3 && `#${entry.rank}`}
                </div>
                
                <div className="entry-info">
                  <span className="entry-username">{entry.username}</span>
                  <span className="entry-level">Level {entry.level}</span>
                </div>
                
                <div className="entry-points">
                  {(entry.points || 0).toLocaleString()} pts
                </div>
                
                {entry.badge && (
                  <div className="entry-badge">{entry.badge}</div>
                )}
              </motion.div>
            ))
          )}
        </div>

        <div className="leaderboard-footer">
          <p>🎯 Earn points by watching streams, chatting, and participating in activities!</p>
        </div>
      </div>
    </motion.section>
  );
};

export default Leaderboard;
