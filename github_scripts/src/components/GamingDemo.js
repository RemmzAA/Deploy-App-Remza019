import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import MatrixRain from './MatrixRain';
import './GamingDemo.css';

const GamingDemo = () => {
  const [isLive, setIsLive] = useState(true);
  const [viewerCount, setViewerCount] = useState(247);
  const [followerCount, setFollowerCount] = useState(2100);

  // Simulate live viewer count updates
  useEffect(() => {
    const interval = setInterval(() => {
      setViewerCount(prev => prev + Math.floor(Math.random() * 20 - 10));
      setFollowerCount(prev => prev + Math.floor(Math.random() * 5));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const recentStreams = [
    {
      id: 1,
      title: 'Competitive Racing - Road to Grand Champion',
      game: 'FORTNITE ROCKET RACING',
      duration: '2h 45m',
      views: '3.2K',
      thumbnail: 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400&h=225&fit=crop'
    },
    {
      id: 2,
      title: 'Solo Victory Royales',
      game: 'FORTNITE',
      duration: '1h 58m',
      views: '2.8K',
      thumbnail: 'https://images.unsplash.com/photo-1511512578047-dfb367046420?w=400&h=225&fit=crop'
    },
    {
      id: 3,
      title: 'Multiplayer Matches',
      game: 'CALL OF DUTY',
      duration: '1h 32m',
      views: '1.9K',
      thumbnail: 'https://images.unsplash.com/photo-1552820728-8b83bb6b773f?w=400&h=225&fit=crop'
    },
    {
      id: 4,
      title: 'Warzone Gameplay',
      game: 'MODERN WARFARE',
      duration: '2h 18m',
      views: '2.1K',
      thumbnail: 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400&h=225&fit=crop'
    }
  ];

  const schedule = [
    { day: 'MON', time: '19:00', game: 'FORTNITE' },
    { day: 'TUE', time: '20:00', game: 'COD Multiplayer' },
    { day: 'WED', time: '19:30', game: 'ROCKET RACING' },
    { day: 'THU', time: '20:00', game: 'MODERN WARFARE' },
    { day: 'FRI', time: '19:00', game: 'FORTNITE Weekend' },
    { day: 'SAT', time: '18:00', game: 'ROCKET RACING Tournament' },
    { day: 'SUN', time: 'REST', game: 'No Stream' }
  ];

  return (
    <div className="gaming-demo">
      {/* Matrix Rain Background */}
      <div className="matrix-background-demo">
        <MatrixRain />
      </div>
      
      <motion.header 
        className="demo-header gaming-header"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="header-brand">
          <h1>Remza019 Gaming</h1>
          <p>Professional Esports Content Creator</p>
        </div>
        <div className="live-status">
          {isLive ? (
            <div className="live-indicator gaming-live">
              <span className="live-dot"></span>
              LIVE - {viewerCount.toLocaleString()} viewers
            </div>
          ) : (
            <div className="offline-indicator">
              OFFLINE
            </div>
          )}
        </div>
      </motion.header>

      {/* Main Content Container */}
      <div className="container">
        {/* Main Stream/Video Section */}
        <motion.section 
          className="main-content-gaming"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <div className="stream-player matrix-card">
            <div className="video-placeholder">
              <div className="play-button">
                <div className="play-icon">▶</div>
              </div>
              <div className="stream-overlay">
                <h3>LIVE: FORTNITE Battle Royale</h3>
                <p>Victory Royale Hunt - Episode 23</p>
              </div>
            </div>
            <div className="stream-info">
              <div className="stream-stats">
                <div className="stat-item">
                  <span className="stat-number">{viewerCount.toLocaleString()}</span>
                  <span className="stat-label">Live Viewers</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">{followerCount.toLocaleString()}</span>
                  <span className="stat-label">Followers</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">89</span>
                  <span className="stat-label">Streams</span>
                </div>
              </div>
              <button className="matrix-button follow-btn">
                Follow Channel
              </button>
            </div>
          </div>
        </motion.section>

        {/* Gaming Bio Section - REAL INFORMATION */}
        <motion.section 
          className="gaming-bio matrix-card"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          <h2>About Remza019</h2>
          <div className="bio-content">
            <p>🎮 Casual gamer focused on FORTNITE, Call of Duty, and Modern Warfare gameplay</p>
            <p>🏎️ <strong>FORTNITE ROCKET RACING competitor</strong> - the ONLY game I compete in tournaments</p>
            <p>🎯 Real gameplay sessions, no fake content or exaggerated claims</p>
            <p>📺 Honest gaming content with {viewerCount} real viewers and {(followerCount/1000).toFixed(1)}K followers</p>
            <p>🇷🇸 Based in Serbia, streaming in CET timezone</p>
            <p>❌ <strong>NOT an esports representative</strong> - just a passionate gamer</p>
          </div>
        </motion.section>

        {/* Recent Streams */}
        <motion.section 
          className="recent-streams"
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <h2>🎮 Recent Streams</h2>
          <div className="streams-grid">
            {recentStreams.map((stream, index) => (
              <motion.div 
                key={stream.id}
                className="stream-card matrix-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.6 + 0.1 * index }}
                whileHover={{ scale: 1.05 }}
              >
                <div className="stream-thumbnail">
                  <img src={stream.thumbnail} alt={stream.title} />
                  <div className="stream-duration">{stream.duration}</div>
                  <div className="stream-views">{stream.views} views</div>
                </div>
                <div className="stream-details">
                  <h4>{stream.title}</h4>
                  <p className="stream-game">🎯 {stream.game}</p>
                  <button className="matrix-button watch-btn">
                    Watch Highlights
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Stream Schedule */}
        <motion.section 
          className="stream-schedule"
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <h2>📅 Weekly Schedule (CET)</h2>
          <div className="schedule-grid">
            {schedule.map((slot, index) => (
              <motion.div 
                key={slot.day}
                className={`schedule-card matrix-card ${slot.day === 'SUN' ? 'rest-day' : ''}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.8 + 0.05 * index }}
              >
                <div className="schedule-day">{slot.day}</div>
                <div className="schedule-time">{slot.time}</div>
                <div className="schedule-game">{slot.game}</div>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Community Section */}
        <motion.section 
          className="community-section"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
        >
          <h2>🎯 Join the Community</h2>
          <div className="community-links">
            <motion.button 
              className="matrix-button community-btn discord"
              whileHover={{ scale: 1.05 }}
              onClick={() => window.open('https://discord.gg/remza019', '_blank')}
            >
              💬 Discord Server
            </motion.button>
            <motion.button 
              className="matrix-button community-btn youtube"
              whileHover={{ scale: 1.05 }}
              onClick={() => window.open('http://www.youtube.com/@remza019', '_blank')}
            >
              📺 YouTube Channel
            </motion.button>
            <motion.button 
              className="matrix-button community-btn youtube-follow"
              whileHover={{ scale: 1.05 }}
              onClick={() => window.open('http://www.youtube.com/@remza019?sub_confirmation=1', '_blank')}
            >
              🔔 Follow Channel
            </motion.button>
            <motion.button 
              className="matrix-button community-btn twitch"
              whileHover={{ scale: 1.05 }}
              onClick={() => window.open('https://www.twitch.tv/remza019', '_blank')}
            >
              🟣 Twitch Channel
            </motion.button>
            <motion.button 
              className="matrix-button community-btn twitter"
              whileHover={{ scale: 1.05 }}
              onClick={() => window.open('https://twitter.com/remza019', '_blank')}
            >
              🐦 Twitter/X
            </motion.button>
          </div>
        </motion.section>
      </div>
    </div>
  );
};

export default GamingDemo;