import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TwitchVODs.css';

const TwitchVODs = ({ limit = 12 }) => {
  const [vods, setVods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchVODs();
  }, [limit]);

  const fetchVODs = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/twitch/vods?limit=${limit}`);
      setVods(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching VODs:', err);
      setError('Failed to load past broadcasts');
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (duration) => {
    // Duration comes as "1h30m20s" format
    const hours = duration.match(/(\d+)h/);
    const minutes = duration.match(/(\d+)m/);
    const seconds = duration.match(/(\d+)s/);

    const h = hours ? parseInt(hours[1]) : 0;
    const m = minutes ? parseInt(minutes[1]) : 0;
    const s = seconds ? parseInt(seconds[1]) : 0;

    if (h > 0) {
      return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="vods-loading">
        <div className="loading-spinner"></div>
        <p>Loading past broadcasts...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="vods-error">
        <p>⚠️ {error}</p>
        <button onClick={fetchVODs}>Retry</button>
      </div>
    );
  }

  if (vods.length === 0) {
    return (
      <div className="vods-empty">
        <h3>📹 No past broadcasts available</h3>
        <p>Check back later for recorded streams!</p>
      </div>
    );
  }

  return (
    <div className="twitch-vods-container">
      <div className="vods-header">
        <h2>📹 Past Broadcasts</h2>
        <p className="vods-count">{vods.length} video{vods.length !== 1 ? 's' : ''}</p>
      </div>

      <div className="vods-grid">
        {vods.map((vod) => (
          <a 
            key={vod.id} 
            href={vod.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="vod-card"
          >
            <div className="vod-thumbnail-wrapper">
              <img 
                src={vod.thumbnail_url.replace('%{width}', '480').replace('%{height}', '270')}
                alt={vod.title}
                className="vod-thumbnail"
                loading="lazy"
              />
              <div className="vod-duration-badge">
                {formatDuration(vod.duration)}
              </div>
              <div className="vod-play-overlay">
                <div className="play-icon">▶</div>
              </div>
            </div>

            <div className="vod-info">
              <h3 className="vod-title">{vod.title}</h3>
              <div className="vod-meta">
                <span className="vod-date">📅 {formatDate(vod.created_at)}</span>
                <span className="vod-views">👁️ {vod.view_count?.toLocaleString()} views</span>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
};

export default TwitchVODs;
