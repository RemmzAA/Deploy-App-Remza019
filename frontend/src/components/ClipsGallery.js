import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ClipsGallery.css';

const ClipsGallery = ({ user }) => {
  const [clips, setClips] = useState([]);
  const [timeRange, setTimeRange] = useState('week');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrendingClips();
  }, [timeRange]);

  const fetchTrendingClips = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/clips/trending?time_range=${timeRange}&limit=12`);
      setClips(response.data.clips);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching clips:', error);
      setLoading(false);
    }
  };

  const handleReact = async (clipId, reactionType) => {
    if (!user) {
      alert('Please login to react!');
      return;
    }

    try {
      await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/clips/${clipId}/react`, {
        user_id: user.id,
        clip_id: clipId,
        reaction_type: reactionType
      });
      fetchTrendingClips();
    } catch (error) {
      console.error('Error reacting to clip:', error);
    }
  };

  if (loading) {
    return <div className="clips-loading">Loading clips...</div>;
  }

  return (
    <div className="clips-gallery-container">
      <div className="clips-header">
        <h2>🎬 Trending Clips & Highlights</h2>
        <div className="time-range-selector">
          <button 
            className={timeRange === 'day' ? 'active' : ''}
            onClick={() => setTimeRange('day')}
          >
            Today
          </button>
          <button 
            className={timeRange === 'week' ? 'active' : ''}
            onClick={() => setTimeRange('week')}
          >
            This Week
          </button>
          <button 
            className={timeRange === 'month' ? 'active' : ''}
            onClick={() => setTimeRange('month')}
          >
            This Month
          </button>
          <button 
            className={timeRange === 'all' ? 'active' : ''}
            onClick={() => setTimeRange('all')}
          >
            All Time
          </button>
        </div>
      </div>

      {clips.length === 0 ? (
        <div className="no-clips">
          <p>No clips available yet. Be the first to create one!</p>
        </div>
      ) : (
        <div className="clips-grid">
          {clips.map((clip) => (
            <div key={clip.clip_id} className="clip-card">
              <div className="clip-thumbnail-wrapper">
                <img 
                  src={clip.thumbnail_url || '/placeholder-clip.jpg'} 
                  alt={clip.title}
                  className="clip-thumbnail"
                />
                <div className="clip-duration">{clip.duration}s</div>
                {clip.is_highlight && (
                  <div className="highlight-badge">⭐ HIGHLIGHT</div>
                )}
              </div>

              <div className="clip-info">
                <h3 className="clip-title">{clip.title}</h3>
                <p className="clip-creator">by {clip.creator_name}</p>

                <div className="clip-stats">
                  <span className="stat">👁️ {clip.views || 0}</span>
                  <span className="stat">❤️ {clip.likes || 0}</span>
                </div>

                <div className="clip-reactions">
                  <button 
                    className="reaction-btn"
                    onClick={() => handleReact(clip.clip_id, 'like')}
                    title="Like"
                  >
                    👍
                  </button>
                  <button 
                    className="reaction-btn"
                    onClick={() => handleReact(clip.clip_id, 'love')}
                    title="Love"
                  >
                    ❤️
                  </button>
                  <button 
                    className="reaction-btn"
                    onClick={() => handleReact(clip.clip_id, 'fire')}
                    title="Fire"
                  >
                    🔥
                  </button>
                  <button 
                    className="reaction-btn"
                    onClick={() => handleReact(clip.clip_id, 'laugh')}
                    title="Laugh"
                  >
                    😂
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ClipsGallery;