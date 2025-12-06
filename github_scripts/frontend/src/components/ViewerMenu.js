import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Cookies from 'js-cookie';
import { useLanguage } from '../i18n/LanguageContext';
import './ViewerMenu.css';

const ViewerMenu = () => {
  const { t } = useLanguage();
  const [user, setUser] = useState(null);
  const [points, setPoints] = useState(0);
  const [level, setLevel] = useState(1);
  const [showLogin, setShowLogin] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [unlockedFeatures, setUnlockedFeatures] = useState(['chat']);
  const [chatWs, setChatWs] = useState(null);
  
  // 🍪 AUTO-LOGIN: Load user from Cookie OR localStorage on mount
  useEffect(() => {
    // Priority 1: Check Cookie (secure, persistent)
    const cookieUser = Cookies.get('viewer_user');
    const cookieToken = Cookies.get('viewer_token');
    
    if (cookieUser && cookieToken) {
      try {
        const userData = JSON.parse(cookieUser);
        console.log('✅ User auto-logged in from COOKIE:', userData);
        setUser(userData);
        setPoints(userData.points || 0);
        setLevel(userData.level || 1);
        
        // Sync to localStorage as backup
        localStorage.setItem('viewer_user', cookieUser);
        localStorage.setItem('viewer_points', userData.points || 0);
        localStorage.setItem('viewer_level', userData.level || 1);
        localStorage.setItem('viewer_token', cookieToken);
        
        return; // Cookie found, skip localStorage check
      } catch (error) {
        console.error('Failed to parse cookie user:', error);
        Cookies.remove('viewer_user');
        Cookies.remove('viewer_token');
      }
    }
    
    // Priority 2: Fallback to localStorage
    const savedUser = localStorage.getItem('viewer_user');
    const savedPoints = localStorage.getItem('viewer_points');
    const savedLevel = localStorage.getItem('viewer_level');
    
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        console.log('✅ User loaded from localStorage:', userData);
        setUser(userData);
        setPoints(savedPoints ? parseInt(savedPoints) : 0);
        setLevel(savedLevel ? parseInt(savedLevel) : 1);
        
        // Upgrade to Cookie for persistence
        Cookies.set('viewer_user', savedUser, { expires: 365, sameSite: 'Lax' });
        if (localStorage.getItem('viewer_token')) {
          Cookies.set('viewer_token', localStorage.getItem('viewer_token'), { expires: 365, sameSite: 'Lax' });
        }
      } catch (error) {
        console.error('Failed to parse saved user:', error);
        localStorage.removeItem('viewer_user');
      }
    }
  }, []);
  
  // Save user to localStorage whenever it changes
  useEffect(() => {
    if (user) {
      localStorage.setItem('viewer_user', JSON.stringify(user));
      localStorage.setItem('viewer_points', points.toString());
      localStorage.setItem('viewer_level', level.toString());
      console.log('💾 User saved to localStorage:', user);
    }
  }, [user, points, level]);

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

  // Dynamic configs - loaded from backend
  const [levelSystem, setLevelSystem] = useState({});
  const [activities, setActivities] = useState([]);
  const [viewerSystemEnabled, setViewerSystemEnabled] = useState(true);
  
  // Load viewer system config from backend
  useEffect(() => {
    const loadViewerConfig = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/viewer-config/current`);
        const data = await response.json();
        
        if (data.success && data.config) {
          console.log('✅ Viewer config loaded from backend:', data.config);
          
          // Set level system
          setLevelSystem(data.config.level_system || {});
          
          // Convert points_config to activities array
          const pointsConfig = data.config.points_config || {};
          const activitiesArray = Object.entries(pointsConfig)
            .filter(([_, config]) => config.enabled && !_.includes('registration'))
            .map(([type, config]) => ({
              type: type,
              name: config.name,
              points: config.points,
              icon: config.icon
            }));
          setActivities(activitiesArray);
          
          // Set system settings
          setViewerSystemEnabled(data.config.system_settings?.enable_viewer_system ?? true);
        } else {
          // Use fallback defaults
          console.warn('⚠️ Using fallback viewer config');
          setLevelSystem({
            1: { required: 0, name: "Rookie Viewer", features: ['chat'], icon: '🌱' },
            2: { required: 100, name: "Active Gamer", features: ['chat', 'polls'], icon: '🎮' },
            3: { required: 250, name: "Gaming Fan", features: ['chat', 'polls', 'predictions'], icon: '⭐' },
            4: { required: 500, name: "Stream Supporter", features: ['chat', 'polls', 'predictions', 'highlights'], icon: '💎' },
            5: { required: 1000, name: "VIP Viewer", features: ['chat', 'polls', 'predictions', 'highlights', 'private_chat'], icon: '👑' },
            6: { required: 2000, name: "Gaming Legend", features: ['chat', 'polls', 'predictions', 'highlights', 'private_chat', 'moderator'], icon: '🏆' }
          });
          setActivities([
            { type: 'stream_view', name: 'Stream View (5min)', points: 5, icon: '📺' },
            { type: 'chat_message', name: 'Chat Message', points: 2, icon: '💬' },
            { type: 'like_video', name: 'Like Video', points: 3, icon: '👍' },
            { type: 'share_stream', name: 'Share Stream', points: 10, icon: '🔗' },
            { type: 'subscribe', name: 'Subscribe', points: 25, icon: '🔔' },
            { type: 'daily_visit', name: 'Daily Visit', points: 5, icon: '📅' },
            { type: 'vote_poll', name: 'Vote in Poll', points: 3, icon: '🗳️' },
            { type: 'stream_prediction', name: 'Stream Prediction', points: 7, icon: '🎯' }
          ]);
        }
      } catch (error) {
        console.error('❌ Failed to load viewer config:', error);
      }
    };
    
    loadViewerConfig();
  }, []);

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
          email: email
        }),
      });

      const data = await response.json();

      if (data.success && data.viewer) {
        const newUser = {
          id: data.viewer.id,
          username: data.viewer.username,
          email: data.viewer.email,
          points: data.viewer.points || 0,
          level: data.viewer.level || 1,
          joinedAt: new Date().toISOString(),
          lastActive: new Date().toISOString()
        };
        
        setUser(newUser);
        setPoints(data.viewer.points || 0);
        setLevel(data.viewer.level || 1);
        setShowLogin(false);
        
        // 🍪 SAVE TO COOKIE (365 days expiry for persistent login)
        Cookies.set('viewer_user', JSON.stringify(newUser), { 
          expires: 365, 
          sameSite: 'Lax',
          secure: window.location.protocol === 'https:'
        });
        
        // Generate simple token (backend should provide real token)
        const token = btoa(`${newUser.id}:${Date.now()}`);
        Cookies.set('viewer_token', token, { 
          expires: 365, 
          sameSite: 'Lax',
          secure: window.location.protocol === 'https:'
        });
        
        // Also save to localStorage as backup
        localStorage.setItem('viewer_user', JSON.stringify(newUser));
        localStorage.setItem('viewer_token', token);
        
        console.log('✅ Viewer registered & saved to COOKIE:', newUser);
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
        
        // 🍪 Save to cookie
        Cookies.set('viewer_user', JSON.stringify(newUser), { expires: 365, sameSite: 'Lax' });
        
        console.log('ℹ️ User already exists, logged in & saved to COOKIE');
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

  // 🍪 LOGOUT: Clear cookies and localStorage
  const handleLogout = () => {
    // Clear cookies
    Cookies.remove('viewer_user');
    Cookies.remove('viewer_token');
    
    // Clear localStorage
    localStorage.removeItem('viewer_user');
    localStorage.removeItem('viewer_token');
    localStorage.removeItem('viewer_points');
    localStorage.removeItem('viewer_level');
    
    // Reset state
    setUser(null);
    setPoints(0);
    setLevel(1);
    setUnlockedFeatures(['chat']);
    
    console.log('✅ User logged out, cookies cleared');
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
              <div className="feature-card" data-tooltip="Earn 5 points for every 10 minutes of stream watching. Build your points by being an active viewer!">
                <span className="feature-icon">📺</span>
                <h4>{t('watchEarn')}</h4>
                <p>{t('watchEarnDesc')}</p>
              </div>
              
              <div className="feature-card" data-tooltip="Participate in live chat and earn 2 points per message. Connect with other viewers in real-time!">
                <span className="feature-icon">💬</span>
                <h4>{t('liveChat')}</h4>
                <p>{t('liveChatDesc')}</p>
              </div>
              
              <div className="feature-card" data-tooltip="Vote in live polls and make predictions. Earn 3 points for each poll participation!">
                <span className="feature-icon">🗳️</span>
                <h4>{t('votePredict')}</h4>
                <p>{t('votePredictDesc')}</p>
              </div>
              
              <div className="feature-card" data-tooltip="Reach Level 4 to unlock VIP features: private chat, custom emotes, and priority support!">
                <span className="feature-icon">⭐</span>
                <h4>{t('vipAccess')}</h4>
                <p>{t('vipAccessDesc')}</p>
              </div>
              
              <div className="feature-card" data-tooltip="Progress through 6 levels: Rookie Viewer → Active Watcher → Engaged Fan → VIP Member → Elite Supporter → Gaming Legend!">
                <span className="feature-icon">🏆</span>
                <h4>{t('levelSystem')}</h4>
                <p>{t('levelSystemDesc')}</p>
              </div>
              
              <div className="feature-card" data-tooltip="Get special perks and badges as you level up. Unlock moderator access at Level 6!">
                <span className="feature-icon">🎯</span>
                <h4>{t('rewards')}</h4>
                <p>{t('rewardsDesc')}</p>
              </div>
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
          <ActivitiesTab activities={activities} addPoints={addPoints} />
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
      <h4>💬 REMZA019 Gaming Chat</h4>
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
const ActivitiesTab = ({ activities, addPoints }) => {
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
      const shareUrl = 'https://deployed-app.preview.emergentagent.com';
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