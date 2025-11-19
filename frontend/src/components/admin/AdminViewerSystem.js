import React, { useState, useEffect } from 'react';
import './AdminViewerSystem.css';

const AdminViewerSystem = () => {
  const [activeTab, setActiveTab] = useState('points');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  
  // Viewer config state
  const [pointsConfig, setPointsConfig] = useState({});
  const [levelSystem, setLevelSystem] = useState({});
  const [rewards, setRewards] = useState({});
  const [systemSettings, setSystemSettings] = useState({});
  const [stats, setStats] = useState(null);

  // Load viewer config on mount
  useEffect(() => {
    loadViewerConfig();
    loadStats();
  }, []);

  const loadViewerConfig = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/viewer-config/current`);
      const data = await response.json();
      
      if (data.success && data.config) {
        setPointsConfig(data.config.points_config || {});
        setLevelSystem(data.config.level_system || {});
        setRewards(data.config.rewards || {});
        setSystemSettings(data.config.system_settings || {});
        console.log('✅ Viewer config loaded');
      }
    } catch (error) {
      console.error('❌ Failed to load viewer config:', error);
      showMessage('Failed to load configuration', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/viewer-config/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      
      if (data.success) {
        setStats(data.stats);
        console.log('✅ Stats loaded:', data.stats);
      }
    } catch (error) {
      console.error('❌ Failed to load stats:', error);
    }
  };

  const showMessage = (text, type = 'success') => {
    setMessage({ text, type });
    setTimeout(() => setMessage(''), 3000);
  };

  const savePointsConfig = async () => {
    try {
      setSaving(true);
      const token = localStorage.getItem('admin_token');
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/viewer-config/points/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ points_config: pointsConfig })
      });
      
      const data = await response.json();
      
      if (data.success) {
        showMessage('✅ Points configuration saved!', 'success');
        loadViewerConfig();
      } else {
        showMessage('❌ Failed to save points config', 'error');
      }
    } catch (error) {
      console.error('❌ Save error:', error);
      showMessage('❌ Error saving configuration', 'error');
    } finally {
      setSaving(false);
    }
  };

  const saveLevelSystem = async () => {
    try {
      setSaving(true);
      const token = localStorage.getItem('admin_token');
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/viewer-config/levels/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ level_system: levelSystem })
      });
      
      const data = await response.json();
      
      if (data.success) {
        showMessage('✅ Level system saved!', 'success');
        loadViewerConfig();
      } else {
        showMessage('❌ Failed to save level system', 'error');
      }
    } catch (error) {
      console.error('❌ Save error:', error);
      showMessage('❌ Error saving level system', 'error');
    } finally {
      setSaving(false);
    }
  };

  const saveSystemSettings = async () => {
    try {
      setSaving(true);
      const token = localStorage.getItem('admin_token');
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/viewer-config/settings/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ system_settings: systemSettings })
      });
      
      const data = await response.json();
      
      if (data.success) {
        showMessage('✅ System settings saved!', 'success');
        loadViewerConfig();
      } else {
        showMessage('❌ Failed to save settings', 'error');
      }
    } catch (error) {
      console.error('❌ Save error:', error);
      showMessage('❌ Error saving settings', 'error');
    } finally {
      setSaving(false);
    }
  };

  const updatePointsActivity = (activityKey, field, value) => {
    setPointsConfig(prev => ({
      ...prev,
      [activityKey]: {
        ...prev[activityKey],
        [field]: value
      }
    }));
  };

  const updateLevel = (levelNum, field, value) => {
    setLevelSystem(prev => ({
      ...prev,
      [levelNum]: {
        ...prev[levelNum],
        [field]: value
      }
    }));
  };

  const updateSystemSetting = (setting, value) => {
    setSystemSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  if (loading) {
    return (
      <div className="viewer-system-loading">
        <div className="spinner"></div>
        <p>Loading Viewer System Configuration...</p>
      </div>
    );
  }

  return (
    <div className="admin-viewer-system">
      <div className="viewer-system-header">
        <h2>🎮 Viewer System Management</h2>
        <p>Complete control over points, levels, and rewards</p>
      </div>

      {message && (
        <div className={`viewer-message ${message.type}`}>
          {message.text}
        </div>
      )}

      {/* Statistics Dashboard */}
      {stats && (
        <div className="viewer-stats-overview">
          <div className="stat-card">
            <div className="stat-icon">👥</div>
            <div className="stat-info">
              <div className="stat-value">{stats.total_viewers}</div>
              <div className="stat-label">Total Viewers</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">⭐</div>
            <div className="stat-info">
              <div className="stat-value">{stats.total_points_awarded}</div>
              <div className="stat-label">Points Awarded</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🎯</div>
            <div className="stat-info">
              <div className="stat-value">{stats.total_activities}</div>
              <div className="stat-label">Total Activities</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🆕</div>
            <div className="stat-info">
              <div className="stat-value">{stats.recent_registrations_7d}</div>
              <div className="stat-label">New (7 days)</div>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="viewer-tabs">
        <button 
          className={`viewer-tab ${activeTab === 'points' ? 'active' : ''}`}
          onClick={() => setActiveTab('points')}
        >
          ⭐ Points System
        </button>
        <button 
          className={`viewer-tab ${activeTab === 'levels' ? 'active' : ''}`}
          onClick={() => setActiveTab('levels')}
        >
          🏆 Level System
        </button>
        <button 
          className={`viewer-tab ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
      </div>

      {/* Tab Content */}
      <div className="viewer-tab-content">
        
        {/* POINTS SYSTEM TAB */}
        {activeTab === 'points' && (
          <div className="points-management">
            <h3>Points Configuration</h3>
            <p>Configure how many points viewers earn for each activity</p>
            
            <div className="points-list">
              {Object.entries(pointsConfig).map(([activityKey, config]) => (
                <div key={activityKey} className="point-activity-card">
                  <div className="activity-header">
                    <span className="activity-icon">{config.icon}</span>
                    <input
                      type="text"
                      className="activity-name-input"
                      value={config.name}
                      onChange={(e) => updatePointsActivity(activityKey, 'name', e.target.value)}
                      placeholder="Activity Name"
                    />
                  </div>
                  
                  <div className="activity-controls">
                    <div className="control-group">
                      <label>Points:</label>
                      <input
                        type="number"
                        className="points-input"
                        value={config.points}
                        onChange={(e) => updatePointsActivity(activityKey, 'points', parseInt(e.target.value) || 0)}
                        min="-1000"
                        max="1000"
                      />
                    </div>
                    
                    <div className="control-group">
                      <label>Enabled:</label>
                      <input
                        type="checkbox"
                        checked={config.enabled}
                        onChange={(e) => updatePointsActivity(activityKey, 'enabled', e.target.checked)}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <button 
              className="save-button"
              onClick={savePointsConfig}
              disabled={saving}
            >
              {saving ? '💾 Saving...' : '💾 Save Points Configuration'}
            </button>
          </div>
        )}

        {/* LEVEL SYSTEM TAB */}
        {activeTab === 'levels' && (
          <div className="levels-management">
            <h3>Level System Configuration</h3>
            <p>Define level requirements and features</p>
            
            <div className="levels-list">
              {Object.entries(levelSystem).sort((a, b) => parseInt(a[0]) - parseInt(b[0])).map(([levelNum, config]) => (
                <div key={levelNum} className="level-card">
                  <div className="level-header">
                    <span className="level-number">Level {levelNum}</span>
                    <span className="level-icon">{config.icon}</span>
                  </div>
                  
                  <div className="level-controls">
                    <div className="control-group">
                      <label>Level Name:</label>
                      <input
                        type="text"
                        className="level-name-input"
                        value={config.name}
                        onChange={(e) => updateLevel(levelNum, 'name', e.target.value)}
                        placeholder="Level Name"
                      />
                    </div>
                    
                    <div className="control-group">
                      <label>Points Required:</label>
                      <input
                        type="number"
                        className="points-input"
                        value={config.required}
                        onChange={(e) => updateLevel(levelNum, 'required', parseInt(e.target.value) || 0)}
                        min="0"
                        max="100000"
                      />
                    </div>
                    
                    <div className="control-group">
                      <label>Features:</label>
                      <div className="features-badges">
                        {config.features && config.features.map((feature, idx) => (
                          <span key={idx} className="feature-badge">{feature}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <button 
              className="save-button"
              onClick={saveLevelSystem}
              disabled={saving}
            >
              {saving ? '💾 Saving...' : '💾 Save Level System'}
            </button>
          </div>
        )}

        {/* SETTINGS TAB */}
        {activeTab === 'settings' && (
          <div className="settings-management">
            <h3>System Settings</h3>
            <p>Control viewer system features</p>
            
            <div className="settings-list">
              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={systemSettings.enable_viewer_system || false}
                    onChange={(e) => updateSystemSetting('enable_viewer_system', e.target.checked)}
                  />
                  <span>Enable Viewer System</span>
                </label>
                <p className="setting-description">Master switch for entire viewer system</p>
              </div>
              
              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={systemSettings.enable_leaderboard || false}
                    onChange={(e) => updateSystemSetting('enable_leaderboard', e.target.checked)}
                  />
                  <span>Enable Leaderboard</span>
                </label>
                <p className="setting-description">Show top viewers leaderboard</p>
              </div>
              
              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={systemSettings.enable_chat || false}
                    onChange={(e) => updateSystemSetting('enable_chat', e.target.checked)}
                  />
                  <span>Enable Chat</span>
                </label>
                <p className="setting-description">Allow viewers to use chat</p>
              </div>
              
              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={systemSettings.enable_notifications || false}
                    onChange={(e) => updateSystemSetting('enable_notifications', e.target.checked)}
                  />
                  <span>Enable Notifications</span>
                </label>
                <p className="setting-description">Send notifications to viewers</p>
              </div>
              
              <div className="setting-item">
                <label>Max Leaderboard Entries:</label>
                <input
                  type="number"
                  className="number-input"
                  value={systemSettings.max_leaderboard_entries || 50}
                  onChange={(e) => updateSystemSetting('max_leaderboard_entries', parseInt(e.target.value) || 50)}
                  min="10"
                  max="500"
                />
                <p className="setting-description">How many viewers to show on leaderboard</p>
              </div>
              
              <div className="setting-item">
                <label>Daily Login Streak Bonus:</label>
                <input
                  type="number"
                  className="number-input"
                  value={systemSettings.daily_login_streak_bonus || 5}
                  onChange={(e) => updateSystemSetting('daily_login_streak_bonus', parseInt(e.target.value) || 5)}
                  min="0"
                  max="100"
                />
                <p className="setting-description">Bonus points for consecutive daily logins</p>
              </div>
            </div>
            
            <button 
              className="save-button"
              onClick={saveSystemSettings}
              disabled={saving}
            >
              {saving ? '💾 Saving...' : '💾 Save System Settings'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminViewerSystem;
