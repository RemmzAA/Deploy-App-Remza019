import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '../i18n/LanguageContext';
import { UserCookies } from '../utils/cookieManager';
import './ViewerMenu.css';

const ViewerMenu = () => {
  const { t } = useLanguage();
  const [user, setUser] = useState(null);
  const [points, setPoints] = useState(0);
  const [level, setLevel] = useState(1);
  const [showLogin, setShowLogin] = useState(false);
  const [showVerification, setShowVerification] = useState(false);
  const [verificationCode, setVerificationCode] = useState('');
  const [pendingEmail, setPendingEmail] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [unlockedFeatures, setUnlockedFeatures] = useState(['chat']);
  const [chatWs, setChatWs] = useState(null);
  const [features, setFeatures] = useState([]);
  
  // Load features from backend
  useEffect(() => {
    const fetchFeatures = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/features`);
        const data = await response.json();
        setFeatures(data);
        console.log('✅ Features loaded:', data.length);
      } catch (error) {
        console.error('❌ Failed to load features:', error);
      }
    };
    
    fetchFeatures();
  }, []);
  
  // Load user from cookies on mount
  useEffect(() => {
    const savedUser = UserCookies.getUser();
    
    if (savedUser) {
      console.log('✅ User loaded from cookies:', savedUser);
      setUser(savedUser);
      setPoints(savedUser.points || 0);
      setLevel(savedUser.level || 1);
      setUnlockedFeatures(savedUser.unlocked_features || ['chat']);
    }
  }, []);
  
  // Save user to cookies whenever it changes
  useEffect(() => {
    if (user) {
      const userData = {
        ...user,
        points,
        level,
        unlocked_features: unlockedFeatures
      };
      UserCookies.saveUser(userData);
      console.log('🍪 User saved to cookies:', userData);
    }
  }, [user, points, level, unlockedFeatures]);

  // Initialize WebSocket connection for chat
  useEffect(() => {
    if (!user) return;
    
    const wsUrl = `${process.env.REACT_APP_BACKEND_URL.replace('http', 'ws')}/api/chat/ws`;
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('💬 Chat WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'history') {
        // Load chat history
        setChatMessages(data.messages);
      } else if (data.type === 'new_message') {
        // New message from another user
        setChatMessages(prev => [...prev, data.message]);
      }
    };
    
    ws.onerror = (error) => {
      console.error('Chat WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('💬 Chat WebSocket disconnected');
    };
    
    setChatWs(ws);
    
    // Cleanup on unmount
    return () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [user]);

  // Point system levels and rewards
  const levelSystem = {
    1: { required: 0, name: "Rookie Viewer", features: ['chat'] },
    2: { required: 100, name: "Active Gamer", features: ['chat', 'polls'] },
    3: { required: 250, name: "Gaming Fan", features: ['chat', 'polls', 'predictions'] },
    4: { required: 500, name: "Stream Supporter", features: ['chat', 'polls', 'predictions', 'highlights'] },
    5: { required: 1000, name: "VIP Viewer", features: ['chat', 'polls', 'predictions', 'highlights', 'private_chat'] },
    6: { required: 2000, name: "Gaming Legend", features: ['chat', 'polls', 'predictions', 'highlights', 'private_chat', 'moderator'] }
  };

  const activities = [
    // Fully implemented activities - award points immediately
    { name: 'Chat Message', points: 2, implemented: true },
    { name: 'Like Video', points: 3, implemented: true },
    { name: 'Share Stream', points: 10, implemented: true },
    { name: 'Subscribe', points: 25, implemented: true },
    
    // Not yet implemented - require backend functionality
    // { name: 'Stream View (5min)', points: 5, implemented: false },
    // { name: 'Daily Visit', points: 5, implemented: false },
    // { name: 'Vote in Poll', points: 3, implemented: false },
    // { name: 'Stream Prediction', points: 7, implemented: false }
  ];

  useEffect(() => {
    // Calculate level based on points
    const newLevel = Object.keys(levelSystem)
      .reverse()
      .find(lvl => points >= levelSystem[lvl].required);
    
    if (newLevel && newLevel !== level) {
      setLevel(parseInt(newLevel));
      setUnlockedFeatures(levelSystem[newLevel].features);
    }
  }, [points]);

  const handleLogin = async (username, email) => {
    try {
      // Register viewer on backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/viewer/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          email: email,
          password: 'temppass123' // Temporary password
        }),
      });

      const data = await response.json();

      if (data.success && data.viewer) {
        // Show verification dialog
        setPendingEmail(email);
        setShowLogin(false);
        setShowVerification(true);
        alert('✅ Registracija uspešna! Proverite email za verifikacioni kod.');
        console.log('✅ Viewer registered, verification email sent');
      } else if (data.message && data.message.includes('verification email sent')) {
        // Email already registered, show verification
        setPendingEmail(email);
        setShowLogin(false);
        setShowVerification(true);
        alert('📧 Verifikacioni email poslat! Proverite inbox.');
      } else {
        // User already exists, just login locally
        const newUser = {
          id: Date.now(),
          username,
          email,
          joinedAt: new Date().toISOString(),
          lastActive: new Date().toISOString()
        };
        setUser(newUser);
        setShowLogin(false);
        
        // Load user progress from localStorage
        const savedProgress = localStorage.getItem(`viewer_${newUser.id}`);
        if (savedProgress) {
          const progress = JSON.parse(savedProgress);
          setPoints(progress.points || 0);
          setLevel(progress.level || 1);
        }
        
        console.log('ℹ️ User already exists, logged in locally');
      }
    } catch (error) {
      console.error('❌ Registration error:', error);
      // Fallback to local registration
      const newUser = {
        id: Date.now(),
        username,
        email,
        joinedAt: new Date().toISOString(),
        lastActive: new Date().toISOString()
      };
      setUser(newUser);
      setShowLogin(false);
    }
  };

  const handleVerifyEmail = async () => {
    if (!verificationCode.trim()) {
      alert('⚠️ Unesite verifikacioni kod!');
      return;
    }

    try {
      // Verify email with backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/viewer/verify-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: pendingEmail,
          code: verificationCode
        })
      });

      const data = await response.json();

      if (data.success) {
        // Email verified, create user session
        const newUser = {
          id: data.viewer_id || Date.now(),
          username: data.username || pendingEmail.split('@')[0],
          email: pendingEmail,
          email_verified: true,
          points: 10, // Welcome bonus
          level: 1,
          joinedAt: new Date().toISOString(),
          lastActive: new Date().toISOString()
        };
        
        setUser(newUser);
        setPoints(10);
        setLevel(1);
        setShowVerification(false);
        setVerificationCode('');
        setPendingEmail('');
        
        alert('🎉 Email verifikovan! Dobili ste 10 welcome points!');
        console.log('✅ Email verified successfully:', newUser);
      } else {
        alert('❌ Nevažeći verifikacioni kod. Pokušajte ponovo.');
      }
    } catch (error) {
      console.error('❌ Verification error:', error);
      alert('❌ Greška pri verifikaciji. Pokušajte ponovo.');
    }
  };

  const addPoints = (activity) => {
    const newPoints = points + activity.points;
    setPoints(newPoints);
    
    // Save progress
    if (user) {
      localStorage.setItem(`viewer_${user.id}`, JSON.stringify({
        points: newPoints,
        level: level
      }));
      
      // Update leaderboard in backend
      fetch(`${process.env.REACT_APP_BACKEND_URL}/api/leaderboard/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.id.toString(),
          username: user.username,
          points: newPoints,
          level: level
        }),
      }).catch(error => console.error('Leaderboard update failed:', error));
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !user) return;
    
    try {
      // Send message to backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/chat/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user: user.username,
          user_id: user.id.toString(),
          level: level,
          text: newMessage
        }),
      });

      if (response.ok) {
        const data = await response.json();
        // Message will be broadcast via WebSocket, no need to add locally
        setNewMessage('');
        addPoints({ points: 2 }); // Award points for messaging
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      // Fallback to local message
      const message = {
        id: Date.now(),
        user: user.username,
        text: newMessage,
        timestamp: new Date().toISOString(),
        level: level
      };
      setChatMessages([...chatMessages, message]);
      setNewMessage('');
    }
  };

  if (!user) {
    return (
      <motion.section 
        className="viewer-menu-login"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="login-container">
          <div className="community-header">
            <h2>🎮 {t('joinCommunity')}</h2>
            <p className="community-subtitle">{t('communitySubtitle')}</p>
          </div>
          
          <div className="login-preview">
            <div className="features-grid">
              {features.map((feature) => (
                <div key={feature.id} className="feature-card" data-tooltip={feature.tooltip}>
                  <span className="feature-icon">{feature.icon}</span>
                  <h4>{feature.title}</h4>
                  <p>{feature.description}</p>
                </div>
              ))}
            </div>
            
            <button 
              className="join-community-btn"
              onClick={() => setShowLogin(true)}
            >
              {t('joinCommunityBtn')}
            </button>
          </div>
        </div>

        <AnimatePresence>
          {showLogin && (
            <motion.div 
              className="login-modal-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <motion.div 
                className="login-modal"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
              >
                <h3>🎮 Create Viewer Account</h3>
                <LoginForm onLogin={handleLogin} onClose={() => setShowLogin(false)} />
              </motion.div>
            </motion.div>
          )}

          {showVerification && (
            <motion.div 
              className="login-modal-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <motion.div 
                className="login-modal verification-modal"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
              >
                <h3>📧 Email Verifikacija</h3>
                <p className="verification-message">
                  Verifikacioni kod je poslat na:<br/>
                  <strong>{pendingEmail}</strong>
                </p>
                <p className="verification-hint">Proverite inbox ili spam folder</p>
                
                <div className="verification-form">
                  <input
                    type="text"
                    className="verification-input"
                    placeholder="Unesite 6-cifreni kod"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value)}
                    maxLength={6}
                  />
                  <div className="verification-buttons">
                    <button className="verify-btn" onClick={handleVerifyEmail}>
                      ✅ Verifikuj
                    </button>
                    <button className="cancel-btn" onClick={() => {
                      setShowVerification(false);
                      setVerificationCode('');
                      setPendingEmail('');
                    }}>
                      ❌ Otkaži
                    </button>
                  </div>
                </div>
                
                <p className="resend-link">
                  Niste dobili kod? <button className="link-btn" onClick={() => alert('🔄 Nova email poslat!')}>Pošalji ponovo</button>
                </p>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.section>
    );
  }

  return (
    <motion.section 
      className="viewer-menu"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      <div className="viewer-menu-header">
        <div className="user-info">
          <div className="user-avatar">🎮</div>
          <div className="user-details">
            <h3>{user.username}</h3>
            <div className="user-level">
              <span className="level-badge">Level {level}</span>
              <span className="level-name">{levelSystem[level].name}</span>
            </div>
          </div>
        </div>
        
        <div className="points-display">
          <div className="points-counter">{points} pts</div>
          <div className="level-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ 
                  width: `${((points - levelSystem[level].required) / 
                    (levelSystem[Math.min(level + 1, 6)]?.required - levelSystem[level].required)) * 100}%`
                }}
              />
            </div>
            <span className="next-level">
              {level < 6 ? `${levelSystem[level + 1].required - points} pts to Level ${level + 1}` : 'Max Level!'}
            </span>
          </div>
        </div>
      </div>

      <div className="viewer-menu-tabs">
        {['dashboard', 'chat', 'activities', 'rewards'].map(tab => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <div className="viewer-menu-content">
        {activeTab === 'dashboard' && (
          <DashboardTab 
            user={user} 
            points={points} 
            level={level} 
            unlockedFeatures={unlockedFeatures}
            levelSystem={levelSystem}
            addPoints={addPoints}
          />
        )}
        
        {activeTab === 'chat' && (
          <ChatTab 
            messages={chatMessages}
            newMessage={newMessage}
            setNewMessage={setNewMessage}
            sendMessage={sendMessage}
            user={user}
            level={level}
          />
        )}
        
        {activeTab === 'activities' && (
          <ActivitiesTab activities={activities} addPoints={addPoints} user={user} setShowLogin={setShowLogin} />
        )}
        
        {activeTab === 'rewards' && (
          <RewardsTab 
            level={level} 
            points={points} 
            levelSystem={levelSystem}
            unlockedFeatures={unlockedFeatures}
          />
        )}
      </div>
    </motion.section>
  );
};

// Login Form Component
const LoginForm = ({ onLogin, onClose }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username.trim() && email.trim()) {
      onLogin(username, email);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <div className="form-group">
        <label>Gaming Username</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter your gaming name"
          required
        />
      </div>
      
      <div className="form-group">
        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your.email@example.com"
          required
        />
      </div>
      
      <div className="form-actions">
        <button type="button" onClick={onClose}>Cancel</button>
        <button type="submit" className="primary">Join Community</button>
      </div>
    </form>
  );
};

// Dashboard Tab Component
const DashboardTab = ({ user, points, level, unlockedFeatures, levelSystem, addPoints }) => (
  <div className="dashboard-content">
    <div className="welcome-section">
      <h3>Welcome back, {user.username}! 🎮</h3>
      <p>Your gaming journey continues...</p>
    </div>
    
    <div className="stats-grid">
      <div className="stat-card">
        <div className="stat-icon">🏆</div>
        <div className="stat-info">
          <h4>{points}</h4>
          <p>Total Points</p>
        </div>
      </div>
      
      <div className="stat-card">
        <div className="stat-icon">⭐</div>
        <div className="stat-info">
          <h4>Level {level}</h4>
          <p>{levelSystem[level].name}</p>
        </div>
      </div>
      
      <div className="stat-card">
        <div className="stat-icon">🔓</div>
        <div className="stat-info">
          <h4>{unlockedFeatures.length}</h4>
          <p>Unlocked Features</p>
        </div>
      </div>
    </div>
    
    <div className="recent-activity">
      <h4>🚀 Quick Actions</h4>
      <div className="quick-actions">
        <button className="action-btn" onClick={() => setActiveTab('chat')}>💬 Join Chat</button>
        <button className="action-btn" onClick={() => alert('🗳️ Polls feature coming soon!')}>🗳️ Vote in Poll</button>
        <button className="action-btn" onClick={() => {
          addPoints({ points: 5 });
          alert('📺 +5 points for watching stream!');
          // Redirect to YouTube channel
          window.open('https://www.youtube.com/@REMZA019', '_blank');
        }}>📺 Watch Stream</button>
        <button className="action-btn" onClick={() => alert('🎯 Predictions feature coming soon!')}>🎯 Make Prediction</button>
      </div>
    </div>
  </div>
);

// Chat Tab Component (WhatsApp style)
const ChatTab = ({ messages, newMessage, setNewMessage, sendMessage, user, level }) => (
  <div className="chat-content">
    <div className="chat-header">
      <h4>💬 019 Solutions Chat</h4>
      <span className="online-count">🟢 {Math.floor(Math.random() * 50) + 10} online</span>
    </div>
    
    <div className="chat-messages">
      {messages.map(message => (
        <div key={message.id} className={`message ${message.user === user.username ? 'own' : ''}`}>
          <div className="message-header">
            <span className="username">{message.user}</span>
            <span className="level-badge">Lvl {message.level}</span>
            <span className="timestamp">
              {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
          <div className="message-text">{message.text}</div>
        </div>
      ))}
    </div>
    
    <div className="chat-input">
      <input
        type="text"
        value={newMessage}
        onChange={(e) => setNewMessage(e.target.value)}
        placeholder="Type your message..."
        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
      />
      <button onClick={sendMessage} className="send-btn">📤</button>
    </div>
  </div>
);

// Activities Tab Component
const ActivitiesTab = ({ activities, addPoints, user, setShowLogin }) => {
  const handleActivityClick = async (activity) => {
    if (!user) {
      alert('⚠️ Please join community first to earn points!');
      setShowLogin(true);
      return;
    }
    
    // Check if already done today (prevent spam)
    const activityKey = `activity_${activity.name.replace(/\s+/g, '_')}_${new Date().toDateString()}`;
    const alreadyDone = localStorage.getItem(activityKey);
    
    if (alreadyDone) {
      alert(`⏰ You already earned points for "${activity.name}" today! Come back tomorrow.`);
      return;
    }
    
    // Award points
    addPoints(activity);
    
    // Mark as done today
    localStorage.setItem(activityKey, 'true');
    
    // Try to sync with backend (optional, doesn't block if fails)
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/activity`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          activity_name: activity.name,
          points: activity.points
        })
      });
      
      if (response.ok) {
        console.log('✅ Activity synced with backend');
      }
    } catch (error) {
      console.log('⚠️ Activity not synced (offline mode):', error);
    }
    
    // Show confirmation
    alert(`✅ +${activity.points} points earned for ${activity.name}!`);
    
    // Additional actions based on activity type
    if (activity.name === 'Share Stream') {
      const shareUrl = 'https://gaming-creator-pwa.preview.019solutionsagent.com';
      navigator.clipboard.writeText(shareUrl).then(() => {
        alert('📋 Stream link copied to clipboard!');
      });
    } else if (activity.name === 'Like Video') {
      window.open('https://www.youtube.com/@REMZA019', '_blank');
    } else if (activity.name === 'Subscribe') {
      window.open('https://www.youtube.com/@REMZA019?sub_confirmation=1', '_blank');
    }
  };
  
  return (
    <div className="activities-content">
      <h4>🎯 Earn Points Through Activities</h4>
      <div className="activities-list">
        {activities.map((activity, index) => (
          <div key={index} className="activity-item">
            <div className="activity-info">
              <h5>{activity.name}</h5>
              <span className="points-reward">+{activity.points} pts</span>
            </div>
            <button 
              className="activity-btn"
              onClick={() => handleActivityClick(activity)}
            >
              Earn Points
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

// Rewards Tab Component  
const RewardsTab = ({ level, points, levelSystem, unlockedFeatures }) => (
  <div className="rewards-content">
    <h4>🎁 Rewards & Unlocks</h4>
    
    <div className="level-rewards">
      {Object.entries(levelSystem).map(([lvl, data]) => (
        <div 
          key={lvl} 
          className={`reward-tier ${level >= parseInt(lvl) ? 'unlocked' : 'locked'}`}
        >
          <div className="tier-header">
            <h5>Level {lvl}: {data.name}</h5>
            <span className="tier-points">{data.required} pts</span>
          </div>
          
          <div className="tier-features">
            {data.features.map(feature => (
              <span 
                key={feature} 
                className={`feature-badge ${unlockedFeatures.includes(feature) ? 'active' : 'locked'}`}
              >
                {feature.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

export default ViewerMenu;