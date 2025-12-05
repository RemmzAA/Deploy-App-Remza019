import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TwitchPlayer.css';

const TwitchPlayer = () => {
  const [streamStatus, setStreamStatus] = useState(null);
  const [embedUrl, setEmbedUrl] = useState('');
  const [chatUrl, setChatUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showChat, setShowChat] = useState(true);

  useEffect(() => {
    fetchStreamStatus();
    fetchEmbedUrls();
    
    // Poll for status every 60 seconds
    const interval = setInterval(fetchStreamStatus, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchStreamStatus = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/twitch/status`);
      setStreamStatus(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching stream status:', err);
      setError('Failed to load stream status');
    } finally {
      setLoading(false);
    }
  };

  const fetchEmbedUrls = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/twitch/embed-url`);
      setEmbedUrl(response.data.embed_url);
      setChatUrl(response.data.chat_url);
    } catch (err) {
      console.error('Error fetching embed URLs:', err);
    }
  };

  if (loading) {
    return (
      <div className="twitch-player-loading">
        <div className="loading-spinner"></div>
        <p>Loading stream...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="twitch-player-error">
        <p>⚠️ {error}</p>
        <button onClick={fetchStreamStatus}>Retry</button>
      </div>
    );
  }

  return (
    <div className="twitch-player-container">
      {/* Stream Status Banner */}
      <div className={`stream-status-banner ${streamStatus?.is_live ? 'live' : 'offline'}`}>
        <div className="status-indicator">
          {streamStatus?.is_live ? (
            <>
              <span className="live-dot"></span>
              <span className="live-text">🔴 LIVE</span>
            </>
          ) : (
            <>
              <span className="offline-dot"></span>
              <span className="offline-text">⚪ OFFLINE</span>
            </>
          )}
        </div>
        
        {streamStatus?.is_live && (
          <div className="stream-info-banner">
            <span className="viewer-count">👥 {streamStatus.viewer_count?.toLocaleString()} viewers</span>
            <span className="game-name">{streamStatus.game_name}</span>
          </div>
        )}
      </div>

      {/* Player and Chat Layout */}
      <div className="player-layout">
        {/* Twitch Player */}
        <div className={`player-wrapper ${showChat ? 'with-chat' : 'fullwidth'}`}>
          {streamStatus?.is_live ? (
            <iframe
              src={embedUrl}
              height="100%"
              width="100%"
              allowFullScreen
              title="REMZA019 Twitch Stream"
              className="twitch-iframe"
            />
          ) : (
            <div className="offline-placeholder">
              <div className="offline-content">
                <h2>🎮 remza019 is currently offline</h2>
                <p>Stream will start soon! Check back later.</p>
                {streamStatus?.thumbnail_url && (
                  <img 
                    src={streamStatus.thumbnail_url} 
                    alt="Channel thumbnail"
                    className="channel-thumbnail"
                  />
                )}
                <a 
                  href="https://www.twitch.tv/remza019" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="twitch-link-button"
                >
                  Visit Twitch Channel
                </a>
              </div>
            </div>
          )}
          
          {streamStatus?.is_live && streamStatus?.title && (
            <div className="stream-title-overlay">
              <h3>{streamStatus.title}</h3>
            </div>
          )}
        </div>

        {/* Twitch Chat */}
        {showChat && (
          <div className="chat-wrapper">
            <div className="chat-header">
              <span>💬 Chat</span>
              <button 
                onClick={() => setShowChat(false)}
                className="close-chat-btn"
                title="Hide chat"
              >
                ✕
              </button>
            </div>
            <iframe
              src={chatUrl}
              height="100%"
              width="100%"
              title="Twitch Chat"
              className="chat-iframe"
            />
          </div>
        )}
      </div>

      {/* Show Chat Button (when hidden) */}
      {!showChat && (
        <button 
          onClick={() => setShowChat(true)}
          className="show-chat-btn"
        >
          💬 Show Chat
        </button>
      )}
    </div>
  );
};

export default TwitchPlayer;
