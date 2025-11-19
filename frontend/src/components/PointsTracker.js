import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './PointsTracker.css';

const PointsTracker = ({ user, points, level, onPointsUpdate }) => {
  const [showLevelUp, setShowLevelUp] = useState(false);
  const [previousLevel, setPreviousLevel] = useState(level);
  const [recentActivity, setRecentActivity] = useState('');

  const LEVEL_SYSTEM = {
    1: { required: 0, name: "Rookie Viewer", next: 100, color: "#808080" },
    2: { required: 100, name: "Active Gamer", next: 250, color: "#00ff00" },
    3: { required: 250, name: "Gaming Fan", next: 500, color: "#00d9ff" },
    4: { required: 500, name: "Stream Supporter", next: 1000, color: "#ff00ff" },
    5: { required: 1000, name: "VIP Viewer", next: 2000, color: "#ffff00" },
    6: { required: 2000, name: "Gaming Legend", next: 5000, color: "#ff0000" }
  };

  // Detect level up
  useEffect(() => {
    if (level > previousLevel) {
      setShowLevelUp(true);
      setPreviousLevel(level);
      setTimeout(() => setShowLevelUp(false), 3000);
    }
  }, [level, previousLevel]);

  const currentLevelData = LEVEL_SYSTEM[level] || LEVEL_SYSTEM[1];
  const nextLevelPoints = currentLevelData.next;
  const currentLevelPoints = currentLevelData.required;
  const progressPoints = points - currentLevelPoints;
  const pointsNeeded = nextLevelPoints - currentLevelPoints;
  const progress = (progressPoints / pointsNeeded) * 100;

  const recordActivity = async (activityType) => {
    if (!user || !user.id) return;

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/viewer/activity/${user.id}?activity_type=${activityType}`,
        { method: 'POST' }
      );
      const data = await response.json();

      if (data.success && onPointsUpdate) {
        onPointsUpdate({
          points: data.total_points,
          level: data.level,
          levelName: data.level_name
        });
        setRecentActivity(`+${data.points_awarded} points!`);
        setTimeout(() => setRecentActivity(''), 2000);
      }
    } catch (error) {
      console.error('Failed to record activity:', error);
    }
  };

  if (!user) return null;

  return (
    <div className="points-tracker">
      {/* Level Up Animation */}
      <AnimatePresence>
        {showLevelUp && (
          <motion.div
            className="level-up-notification"
            initial={{ opacity: 0, scale: 0.5, y: 50 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.5, y: -50 }}
            transition={{ duration: 0.5 }}
          >
            <div className="level-up-content">
              <span className="level-up-icon">🎉</span>
              <h3>LEVEL UP!</h3>
              <p>{currentLevelData.name}</p>
              <span className="level-badge">Level {level}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Recent Activity Notification */}
      <AnimatePresence>
        {recentActivity && (
          <motion.div
            className="recent-activity-notification"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
          >
            {recentActivity}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Tracker Card */}
      <motion.div 
        className="tracker-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {/* Header */}
        <div className="tracker-header">
          <div className="user-info">
            <span className="username">{user.username}</span>
            <span className="level-badge" style={{ background: currentLevelData.color }}>
              Lvl {level}
            </span>
          </div>
          <div className="points-display">
            <span className="points-icon">⭐</span>
            <span className="points-value">{points}</span>
          </div>
        </div>

        {/* Level Name */}
        <div className="level-name" style={{ color: currentLevelData.color }}>
          {currentLevelData.name}
        </div>

        {/* Progress Bar */}
        <div className="progress-section">
          <div className="progress-bar-container">
            <motion.div 
              className="progress-bar-fill"
              style={{ 
                width: `${Math.min(progress, 100)}%`,
                background: currentLevelData.color
              }}
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(progress, 100)}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <div className="progress-text">
            {progressPoints} / {pointsNeeded} points to Level {level + 1}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <button
            className="action-btn"
            onClick={() => recordActivity('daily_visit')}
            title="Daily Visit Bonus"
          >
            📅 Daily (+5)
          </button>
          <button
            className="action-btn"
            onClick={() => recordActivity('like_video')}
            title="Like Video"
          >
            👍 Like (+3)
          </button>
          <button
            className="action-btn"
            onClick={() => recordActivity('share_stream')}
            title="Share Stream"
          >
            🔗 Share (+10)
          </button>
          <button
            className="action-btn"
            onClick={() => recordActivity('vote_poll')}
            title="Vote in Poll"
          >
            🗳️ Vote (+3)
          </button>
        </div>

        {/* Achievements Preview */}
        <div className="achievements-preview">
          <h4>🏆 Unlocked Features</h4>
          <div className="features-list">
            {LEVEL_SYSTEM[level]?.features?.map((feature, index) => (
              <span key={index} className="feature-badge">
                {feature}
              </span>
            )) || <span className="feature-badge">chat</span>}
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default PointsTracker;
