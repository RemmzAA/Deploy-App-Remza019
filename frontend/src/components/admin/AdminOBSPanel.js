import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './AdminOBSPanel.css';

const AdminOBSPanel = ({ token }) => {
  const [obsStatus, setObsStatus] = useState(null);
  const [scenes, setScenes] = useState([]);
  const [streamStatus, setStreamStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const API_URL = process.env.REACT_APP_BACKEND_URL;

  // Fetch OBS status
  const fetchOBSStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/obs/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setObsStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch OBS status:', error);
    }
  };

  // Fetch scenes
  const fetchScenes = async () => {
    try {
      const response = await fetch(`${API_URL}/api/obs/scenes`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setScenes(data.scenes || []);
      }
    } catch (error) {
      console.error('Failed to fetch scenes:', error);
    }
  };

  // Fetch stream status
  const fetchStreamStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/obs/stream/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStreamStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch stream status:', error);
    }
  };

  // Load data on mount
  useEffect(() => {
    fetchOBSStatus();
    fetchScenes();
    fetchStreamStatus();
  }, []);

  // Start streaming
  const startStream = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/obs/stream/start`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        const data = await response.json();
        alert(`✅ ${data.message}`);
        fetchStreamStatus();
      } else {
        alert('❌ Failed to start stream');
      }
    } catch (error) {
      alert('❌ Error starting stream');
    } finally {
      setLoading(false);
    }
  };

  // Stop streaming
  const stopStream = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/obs/stream/stop`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        const data = await response.json();
        alert(`✅ ${data.message}`);
        fetchStreamStatus();
      } else {
        alert('❌ Failed to stop stream');
      }
    } catch (error) {
      alert('❌ Error stopping stream');
    } finally {
      setLoading(false);
    }
  };

  // Switch scene
  const switchScene = async (sceneName) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/obs/scenes/${encodeURIComponent(sceneName)}/activate`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        alert(`✅ Switched to ${sceneName}`);
        fetchScenes();
      } else {
        alert('❌ Failed to switch scene');
      }
    } catch (error) {
      alert('❌ Error switching scene');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="obs-panel">
      <motion.h2
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        🎥 OBS Studio Remote Control
      </motion.h2>

      {obsStatus && obsStatus.mock_mode && (
        <div className="mock-warning">
          ⚠️ Running in MOCK MODE - Connect OBS Studio for live control
        </div>
      )}

      {/* OBS Status Card */}
      <motion.div 
        className="obs-status-card"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <h3>📊 OBS Status</h3>
        {obsStatus && (
          <div className="status-grid">
            <div className="status-item">
              <span className="status-label">Connection:</span>
              <span className={`status-value ${obsStatus.connected ? 'connected' : 'disconnected'}`}>
                {obsStatus.connected ? '🟢 Connected' : '🔴 Disconnected'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">OBS Version:</span>
              <span className="status-value">{obsStatus.version || 'N/A'}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Mode:</span>
              <span className="status-value">{obsStatus.mock_mode ? '🧪 Mock' : '🎬 Live'}</span>
            </div>
          </div>
        )}
      </motion.div>

      {/* Stream Controls */}
      <motion.div 
        className="stream-controls-card"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, delay: 0.2 }}
      >
        <h3>📡 Stream Control</h3>
        {streamStatus && (
          <div className="stream-info">
            <div className="stream-status">
              <span className="status-label">Status:</span>
              <span className={`status-badge ${streamStatus.streaming ? 'live' : 'offline'}`}>
                {streamStatus.streaming ? '🔴 LIVE' : '⚫ Offline'}
              </span>
            </div>
            {streamStatus.streaming && (
              <div className="stream-details">
                <p>⏱️ Duration: {streamStatus.stream_duration || '0s'}</p>
                <p>📊 FPS: {streamStatus.fps || 'N/A'}</p>
              </div>
            )}
          </div>
        )}
        <div className="control-buttons">
          <button 
            className="control-btn start-btn"
            onClick={startStream}
            disabled={loading || (streamStatus && streamStatus.streaming)}
          >
            ▶️ Start Stream
          </button>
          <button 
            className="control-btn stop-btn"
            onClick={stopStream}
            disabled={loading || (streamStatus && !streamStatus.streaming)}
          >
            ⏹️ Stop Stream
          </button>
          <button 
            className="control-btn refresh-btn"
            onClick={() => {
              fetchOBSStatus();
              fetchScenes();
              fetchStreamStatus();
            }}
            disabled={loading}
          >
            🔄 Refresh
          </button>
        </div>
      </motion.div>

      {/* Scene Switcher */}
      <motion.div 
        className="scenes-card"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, delay: 0.3 }}
      >
        <h3>🎬 Scenes</h3>
        {scenes.length > 0 ? (
          <div className="scenes-grid">
            {scenes.map((scene, index) => (
              <motion.button
                key={scene.uuid || index}
                className={`scene-card ${scene.is_active ? 'active' : ''}`}
                onClick={() => !scene.is_active && switchScene(scene.name)}
                disabled={loading || scene.is_active}
                whileHover={{ scale: scene.is_active ? 1 : 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <div className="scene-name">{scene.name}</div>
                {scene.is_active && <div className="active-badge">✓ Active</div>}
              </motion.button>
            ))}
          </div>
        ) : (
          <p className="no-data">No scenes available</p>
        )}
      </motion.div>

      {/* Info Section */}
      <div className="info-section">
        <h4>ℹ️ Setup Instructions</h4>
        <ol>
          <li>Install OBS Studio with WebSocket plugin</li>
          <li>Enable WebSocket server in OBS (Tools → WebSocket Server Settings)</li>
          <li>Configure OBS_HOST, OBS_PORT, and OBS_PASSWORD in backend/.env</li>
          <li>Restart backend service to apply changes</li>
        </ol>
      </div>
    </div>
  );
};

export default AdminOBSPanel;
