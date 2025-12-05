import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './YoutubeVideoPlayer.css';

const YoutubeVideoPlayer = () => {
  const [featuredVideo, setFeaturedVideo] = useState(null);
  const [highlightedVideo, setHighlightedVideo] = useState(null);
  const [latestVideos, setLatestVideos] = useState([]);
  const [channelStats, setChannelStats] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [aboutContent, setAboutContent] = useState([]); // ADDED: About content from API

  // Fetch YouTube data from our API
  useEffect(() => {
    const fetchYouTubeData = async () => {
      try {
        setLoading(true);
        console.log('🎬 Fetching YouTube data...');

        // Fetch YouTube API data
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/youtube/latest`);
        console.log('🎬 API Response status:', response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log('🎬 API Response data:', data);
          
          if (Array.isArray(data)) {
            setLatestVideos(data);
            
            if (data.length > 0) {
              setHighlightedVideo(data[0]);
            }
          } else {
            console.warn('🎬 No videos in API response');
          }
        } else {
          console.error('🎬 API Error:', await response.text());
          setError(`Failed to load gaming content (${response.status})`);
        }

        // Fetch featured video for hero section
        const featuredResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/youtube/featured-video`);
        if (featuredResponse.ok) {
          const featuredData = await featuredResponse.json();
          console.log('🎯 Featured video data:', featuredData);
          setFeaturedVideo(featuredData);
        } else {
          console.error('🎯 Featured video error:', await featuredResponse.text());
        }

        // Fetch channel stats
        const statsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/youtube/stats`);
        if (statsResponse.ok) {
          const statsData = await statsResponse.json();
          console.log('🎬 Channel stats:', statsData);
          setChannelStats(statsData);
        } else {
          console.error('🎬 Channel stats error:', await statsResponse.text());
        }

        // Fetch About content from admin API
        console.log('📝 Fetching about content...');
        const aboutResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/content/about`);
        if (aboutResponse.ok) {
          const aboutData = await aboutResponse.json();
          console.log('📝 About content data:', aboutData);
          if (aboutData && aboutData.content) {
            // Convert string format to object format
            const formattedContent = aboutData.content.map((item, index) => {
              if (typeof item === 'string') {
                // Parse emoji and text from string format
                const parts = item.split(' ');
                const icon = parts[0]; // First part is emoji
                const text = parts.slice(1).join(' '); // Rest is text
                return { icon, text, title: '', index };
              }
              return item; // If already object format
            });
            setAboutContent(formattedContent);
          }
        } else {
          console.warn('📝 About content not available, using defaults');
          // Set default about content if API fails
          setAboutContent([
            { icon: '🎮', text: 'Casual gamer focused on FORTNITE gameplay and content creation' },
            { icon: '🏎️', text: 'FORTNITE ROCKET RACING competitor - tournament player' },
            { icon: '🎯', text: 'Real FORTNITE gameplay sessions, no fake content' },
            { icon: '🇷🇸', text: 'Based in Serbia, streaming FORTNITE in CET timezone' }
          ]);
        }

        setLoading(false);
      } catch (error) {
        console.error('🎬 Error fetching data:', error);
        setError('Failed to load gaming content');
        setLoading(false);
      }
    };

    fetchYouTubeData();
    
    // REAL-TIME SSE CONNECTION for admin updates
    const clientId = 'youtube_player_' + Math.random().toString(36).substr(2, 9);
    const eventSource = new EventSource(`${process.env.REACT_APP_BACKEND_URL}/api/sse/${clientId}`);
    
    eventSource.addEventListener('about_content_update', (event) => {
      console.log('📝 Real-time about update received:', event.data);
      const updateData = JSON.parse(event.data);
      
      if (updateData.content) {
        // Format the updated content
        const formattedContent = updateData.content.map((item, index) => {
          if (typeof item === 'string') {
            const parts = item.split(' ');
            const icon = parts[0];
            const text = parts.slice(1).join(' ');
            return { icon, text, title: '', index };
          }
          return item;
        });
        
        setAboutContent(formattedContent);
        console.log('✅ About content updated in real-time');
      }
    });
    
    eventSource.addEventListener('connected', (event) => {
      console.log('🔗 Real-time connection established:', event.data);
    });
    
    eventSource.addEventListener('heartbeat', (event) => {
      // Silent heartbeat
    });
    
    eventSource.onerror = (error) => {
      console.warn('📡 Real-time connection error, will auto-reconnect:', error);
    };
    
    // Cleanup function
    return () => {
      eventSource.close();
      console.log('📡 Real-time connection closed');
    };
  }, []);

  const handlePlayVideo = () => {
    setIsPlaying(true);
  };

  if (loading) {
    return (
      <div className="youtube-player loading">
        <div className="loading-spinner">
          <div className="matrix-spinner"></div>
          <p className="loading-text">🎮 Loading Gaming Content...</p>
          <div className="loading-bar">
            <div className="loading-progress"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="youtube-player error">
        <div className="error-message">
          <div className="error-icon">⚠️</div>
          <h3>🎮 Gaming Content Temporarily Unavailable</h3>
          <p>{error}</p>
          <button 
            className="retry-btn"
            onClick={() => {
              setError('');
              setLoading(true);
              // Retry logic here
              window.location.reload();
            }}
          >
            🔄 Retry Loading
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="youtube-player-container">
      {/* Main Featured Video Player */}
      <motion.div 
        className="featured-player matrix-card"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8 }}
      >
        <div className="video-container">
          {!isPlaying ? (
            // Thumbnail with Play Button
            <div className="video-thumbnail" onClick={handlePlayVideo}>
              <img 
                src={featuredVideo?.thumbnail_url} 
                alt={featuredVideo?.title}
                className="thumbnail-image"
              />
              <div className="play-overlay">
                <div className="play-button">
                  <div className="play-icon">▶</div>
                </div>
                <div className="video-info">
                  <h3>{featuredVideo?.title}</h3>
                  <p>{featuredVideo?.description}</p>
                </div>
              </div>
            </div>
          ) : (
            // YouTube Embedded Player - LOOPED WELCOME VIDEO FROM START
            <iframe
              width="100%"
              height="400"
              src={`${featuredVideo?.embed_url}?autoplay=1&mute=1&loop=1&playlist=${featuredVideo?.video_id}&controls=1&rel=0&modestbranding=1&start=0&enablejsapi=1`}
              title={featuredVideo?.title}
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
              className="youtube-iframe"
            ></iframe>
          )}
        </div>

        {/* Video Stats Overlay */}
        <div className="video-stats-overlay">
          <div className="stat-item">
            <span className="stat-icon">👥</span>
            <span className="stat-value">{channelStats?.subscriber_count}</span>
            <span className="stat-label">Subscribers</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">🎬</span>
            <span className="stat-value">{channelStats?.video_count}</span>
            <span className="stat-label">Videos</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">👁️</span>
            <span className="stat-value">{channelStats?.view_count}</span>
            <span className="stat-label">Total Views</span>
          </div>
        </div>
      </motion.div>

      {/* Latest Videos Sidebar */}
      <motion.div 
        className="latest-videos-sidebar"
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8, delay: 0.3 }}
      >
        <h4>🎮 Latest Gaming Content</h4>
        <div className="videos-list">
          {latestVideos.map((video, index) => (
            <motion.div 
              key={`${video.video_id}-${index}`}
              className="video-item matrix-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 * index }}
              whileHover={{ scale: 1.02 }}
              onClick={() => {
                try {
                  const videoUrl = video.watch_url || `https://www.youtube.com/watch?v=${video.video_id || video.id}`;
                  console.log(`Opening video: ${video.title} - ${videoUrl}`);
                  
                  if (videoUrl && videoUrl.includes('youtube.com')) {
                    window.open(videoUrl, '_blank', 'noopener,noreferrer');
                  } else {
                    console.error('Invalid YouTube URL:', videoUrl);
                  }
                } catch (error) {
                  console.error('Error opening video:', error);
                }
              }}
              style={{ cursor: 'pointer' }}
            >
              <img 
                src={video.thumbnail_url} 
                alt={video.title}
                className="video-thumbnail-small"
                loading="lazy"
                onError={(e) => {
                  e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwIiBoZWlnaHQ9IjkwIiB2aWV3Qm94PSIwIDAgMTIwIDkwIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxMjAiIGhlaWdodD0iOTAiIGZpbGw9IiMwMDAwMDAiLz48cGF0aCBkPSJNNDUgMzBMNzUgNDVMNDUgNjBWMzBaIiBmaWxsPSIjMDBGRjAwIi8+PC9zdmc+';
                }}
                style={{
                  transition: 'opacity 0.3s ease',
                  backgroundColor: '#000',
                }}
              />
              <div className="video-details">
                <h5>{video.title}</h5>
                <div className="video-meta">
                  <span className="views">{video.view_count} views</span>
                  <span className="duration">{video.duration}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Channel Links */}
        <div className="channel-links">
          <motion.a
            href="http://www.youtube.com/@remza019"
            target="_blank"
            rel="noopener noreferrer"
            className="matrix-button youtube-link"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            📺 Visit Channel
          </motion.a>
          <motion.a
            href="http://www.youtube.com/@remza019?sub_confirmation=1"
            target="_blank"
            rel="noopener noreferrer"
            className="matrix-button subscribe-link"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            🔔 Subscribe
          </motion.a>
        </div>
      </motion.div>
      
      {/* About REMZA019 - FILL LEFT COLUMN SPACE */}
      <motion.div 
        className="about-hero-fill"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.6 }}
      >
        <h3 className="about-fill-title">About REMZA019</h3>
        <div className="about-fill-items">
          {aboutContent && aboutContent.length > 0 ? (
            aboutContent.map((item, index) => (
              <div key={index} className="about-fill-item">
                <span className="about-fill-icon">{item.icon}</span>
                <p>{item.text}</p>
              </div>
            ))
          ) : (
            // Fallback static content if API fails
            <>
              <div className="about-fill-item">
                <span className="about-fill-icon">🎮</span>
                <p>Casual gamer focused on <strong>FORTNITE gameplay</strong> and content creation</p>
              </div>
              <div className="about-fill-item">
                <span className="about-fill-icon">🏎️</span>
                <p><strong>FORTNITE ROCKET RACING competitor</strong> - tournament player</p>
              </div>
              <div className="about-fill-item">
                <span className="about-fill-icon">🎯</span>
                <p>Real gameplay, <strong>no fake content</strong></p>
              </div>
              <div className="about-fill-item">
                <span className="about-fill-icon">🇷🇸</span>
                <p>Based in <strong>Serbia</strong>, CET timezone</p>
              </div>
            </>
          )}
        </div>
      </motion.div>
      
    </div>
  );
};

export default YoutubeVideoPlayer;