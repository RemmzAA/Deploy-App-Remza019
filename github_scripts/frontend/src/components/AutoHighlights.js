import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './AutoHighlights.css';

const AutoHighlights = ({ user }) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [highlights, setHighlights] = useState([]);
  const [error, setError] = useState('');

  const analyzeStream = async () => {
    if (!user) {
      setError('Please login to use AI Auto-Highlights');
      return;
    }

    setAnalyzing(true);
    setError('');

    try {
      // Demo chat messages (would come from actual stream in production)
      const demoChatMessages = [
        { timestamp: 120, user: 'Viewer1', text: 'OMG THAT WAS INSANE!' },
        { timestamp: 121, user: 'Viewer2', text: 'POG POG POG' },
        { timestamp: 122, user: 'Viewer3', text: 'CLIP IT!' },
        { timestamp: 125, user: 'Viewer4', text: 'BEST PLAY IVE SEEN' },
        { timestamp: 450, user: 'Viewer5', text: 'WTF HOW DID HE DO THAT' },
        { timestamp: 451, user: 'Viewer6', text: 'THAT AIM THO' },
        { timestamp: 452, user: 'Viewer7', text: 'HOLY MOLY' },
        { timestamp: 780, user: 'Viewer8', text: 'VICTORY ROYALE INCOMING' },
        { timestamp: 782, user: 'Viewer9', text: 'GG GG GG' },
        { timestamp: 785, user: 'Viewer10', text: 'YOU ARE THE GOAT' }
      ];

      const demoGameEvents = [
        { timestamp: 123, type: 'kill', description: 'Headshot elimination with sniper' },
        { timestamp: 455, type: 'achievement', description: 'Triple kill streak' },
        { timestamp: 788, type: 'victory', description: 'Victory Royale achieved' }
      ];

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auto-highlights/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          stream_id: 'demo-stream-' + Date.now(),
          duration_minutes: 15,
          chat_messages: demoChatMessages,
          game_events: demoGameEvents
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze stream');
      }

      const data = await response.json();
      setHighlights(data);
    } catch (err) {
      console.error('Error analyzing highlights:', err);
      setError('Failed to generate highlights. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="auto-highlights-container">
      <motion.div
        className="auto-highlights-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2>🤖 AI Auto-Highlights</h2>
        <p>Automatically detect and create highlight clips using AI analysis</p>
      </motion.div>

      <div className="highlights-controls">
        <button
          className="analyze-btn"
          onClick={analyzeStream}
          disabled={analyzing}
        >
          {analyzing ? '🔄 Analyzing Stream...' : '🎯 Analyze Latest Stream'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {highlights.length > 0 && (
        <motion.div
          className="highlights-grid"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <h3>📽️ Detected Highlights ({highlights.length})</h3>
          {highlights.map((highlight, index) => (
            <motion.div
              key={highlight.highlight_id}
              className="highlight-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className="highlight-header">
                <span className="highlight-number">#{index + 1}</span>
                <span className="highlight-confidence">
                  {(highlight.confidence_score * 100).toFixed(0)}% Confidence
                </span>
              </div>

              <h4>{highlight.title}</h4>
              <p className="highlight-description">{highlight.description}</p>

              <div className="highlight-meta">
                <span className="timestamp">
                  ⏱️ {Math.floor(highlight.start_time / 60)}:{String(Math.floor(highlight.start_time % 60)).padStart(2, '0')} - 
                  {Math.floor(highlight.end_time / 60)}:{String(Math.floor(highlight.end_time % 60)).padStart(2, '0')}
                </span>
                <span className="duration">
                  ⏳ {Math.floor(highlight.end_time - highlight.start_time)}s
                </span>
              </div>

              <p className="highlight-reason">💡 {highlight.reason}</p>

              <div className="highlight-actions">
                <button className="btn-primary" onClick={() => alert('Clip generation coming soon!')}>
                  🎬 Create Clip
                </button>
                <button className="btn-secondary" onClick={() => alert('Share functionality coming soon!')}>
                  🔗 Share
                </button>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {!analyzing && highlights.length === 0 && !error && (
        <div className="empty-state">
          <div className="empty-icon">🎥</div>
          <h3>No highlights analyzed yet</h3>
          <p>Click "Analyze Latest Stream" to automatically detect exciting moments using AI</p>
        </div>
      )}
    </div>
  );
};

export default AutoHighlights;
