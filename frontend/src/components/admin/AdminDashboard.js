import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useLanguage } from '../../i18n/LanguageContext';
import AdminCustomizationPanel from '../AdminCustomizationPanel';
import AdminViewerSystem from './AdminViewerSystem';
import AdminSchedulePanel from './AdminSchedulePanel';
import AdminSiteSettings from './AdminSiteSettings';
import AdminOBSPanel from './AdminOBSPanel';
import AdminStreamlabsPanel from './AdminStreamlabsPanel';
import AdminLicensePanel from './AdminLicensePanel';
import AdminMemberPanel from './AdminMemberPanel';
import './AdminDashboard.css';

const AdminDashboard = ({ token, onLogout }) => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('overview');
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // State for different sections
  const [liveStatus, setLiveStatus] = useState({
    is_live: false,
    current_viewers: '0',
    live_game: ''
  });

  const [channelStats, setChannelStats] = useState({
    subscriber_count: '',
    video_count: '',
    total_views: ''
  });

  const [streamSchedule, setStreamSchedule] = useState([]);
  const [newSchedule, setNewSchedule] = useState({
    day: 'MON',
    time: '19:00',
    game: 'FORTNITE'
  });
  
  const [newStream, setNewStream] = useState({
    title: '',
    game: '',
    duration: '',
    views: '',
    video_url: ''
  });

  const [youtubeSync, setYoutubeSync] = useState({
    last_sync: null,
    sync_active: false,
    next_sync: null
  });

  const [aboutText, setAboutText] = useState('');
  const [aboutTags, setAboutTags] = useState([
    { icon: "🏆", text: "Competitive Player" },
    { icon: "🏎️", text: "Rocket Racing Specialist" },
    { icon: "📺", text: "Content Creator" },
    { icon: "🇷🇸", text: "Serbia (CET)" },
    { icon: "💯", text: "Authentic Gameplay" }
  ]);

  // Theme management state
  const [availableThemes, setAvailableThemes] = useState([
    {
      id: 'matrix_green',
      name: 'Matrix Green',
      description: 'Classic hacker aesthetic',
      preview: {
        primary: 'linear-gradient(135deg, #000000 0%, #0a0a0a 100%)',
        accent: '#10b981',
        text: '#10b981'
      }
    },
    {
      id: 'cyber_purple',
      name: 'Cyber Purple',
      description: 'Futuristic purple vibes',
      preview: {
        primary: 'linear-gradient(135deg, #1a0a2e 0%, #0f051d 100%)',
        accent: '#a855f7',
        text: '#c084fc'
      }
    },
    {
      id: 'neon_blue',
      name: 'Neon Blue',
      description: 'Electric blue energy',
      preview: {
        primary: 'linear-gradient(135deg, #001f3f 0%, #000814 100%)',
        accent: '#06b6d4',
        text: '#22d3ee'
      }
    },
    {
      id: 'fire_red',
      name: 'Fire Red',
      description: 'Intense gaming red',
      preview: {
        primary: 'linear-gradient(135deg, #1a0000 0%, #0a0000 100%)',
        accent: '#ef4444',
        text: '#f87171'
      }
    },
    {
      id: 'toxic_yellow',
      name: 'Toxic Yellow',
      description: 'Radioactive yellow glow',
      preview: {
        primary: 'linear-gradient(135deg, #1a1a00 0%, #0a0a00 100%)',
        accent: '#fbbf24',
        text: '#fde047'
      }
    }
  ]);
  const [currentTheme, setCurrentTheme] = useState(null);
  const [selectedTheme, setSelectedTheme] = useState('matrix_green');
  
  const [siteContent, setSiteContent] = useState({
    about_text: [],
    featured_video: null,
    recent_videos: []
  });

  const [polls, setPolls] = useState([]);
  const [newPoll, setNewPoll] = useState({
    question: '',
    options: ['', '']
  });

  const [predictions, setPredictions] = useState([]);
  const [newPrediction, setNewPrediction] = useState({
    question: '',
    option_a: '',
    option_b: ''
  });
  
  const [aboutContent, setAboutContent] = useState([
    "🎮 Casual gamer focused on FORTNITE gameplay and content creation",
    "🏎️ FORTNITE ROCKET RACING competitor - the ONLY game I compete in tournaments",
    "🎯 Real FORTNITE gameplay sessions, no fake content or exaggerated claims",
    "📺 Honest FORTNITE gaming content with authentic viewers and followers",
    "🇷🇸 Based in Serbia, streaming FORTNITE in CET timezone",
    "❌ NOT an esports representative - just a passionate FORTNITE gamer"
  ]);

  // API helper function
  const apiCall = async (endpoint, method = 'GET', data = null) => {
    const options = {
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}${endpoint}`, options);
    return response.json();
  };
  
  // Save About Content
  const saveAboutContent = async () => {
    try {
      // Split text by newlines and filter empty lines
      const contentLines = aboutText
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);
      
      const result = await apiCall('/api/admin/content/about/update', 'POST', {
        content: contentLines.length > 0 ? contentLines : [aboutText]
      });
      
      if (result.success) {
        alert('✅ About content saved successfully! Refreshing page...');
        // Reload page to show changes
        setTimeout(() => window.location.reload(), 1000);
      }
    } catch (error) {
      console.error('Failed to save about content:', error);
      alert('❌ Failed to save about content: ' + error.message);
    }
  };
  
  // Save About Tags
  const saveAboutTags = async () => {
    try {
      const result = await apiCall('/api/admin/content/tags/update', 'POST', {
        tags: aboutTags
      });
      if (result.success) {
        alert('✅ Tags saved successfully! Refreshing page...');
        // Reload page to show changes
        setTimeout(() => window.location.reload(), 1000);
      }
    } catch (error) {
      console.error('Failed to save tags:', error);
      alert('❌ Failed to save tags: ' + error.message);
    }
  };
  
  // Update tag value
  const updateTag = (index, field, value) => {
    const newTags = [...aboutTags];
    newTags[index][field] = value;
    setAboutTags(newTags);
  };

  // Load About content and tags when entering Content tab
  useEffect(() => {
    if (activeTab === 'content') {
      loadAboutData();
    }
    if (activeTab === 'customization') {
      loadThemes();
      loadCurrentTheme();
    }
  }, [activeTab]);
  
  const loadAboutData = async () => {
    try {
      // Load about content
      const aboutResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/content/about`);
      const aboutData = await aboutResponse.json();
      if (aboutData.content) {
        const contentText = Array.isArray(aboutData.content) 
          ? aboutData.content.join(' • ')
          : aboutData.content;
        setAboutText(contentText);
      }
      
      // Load about tags
      const tagsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/content/tags`);
      const tagsData = await tagsResponse.json();
      if (tagsData.tags && tagsData.tags.length > 0) {
        setAboutTags(tagsData.tags);
      }
    } catch (error) {
      console.error('Failed to load about data:', error);
    }
  };
  
  // Load dashboard data with real-time sync
  useEffect(() => {
    loadDashboardData();
    
    // Real-time live status polling (every 30 seconds)
    const liveStatusInterval = setInterval(() => {
      checkLiveStatus();
    }, 30000); // 30 seconds
    
    return () => clearInterval(liveStatusInterval);
  }, []);
  
  // Real-time live status check
  const checkLiveStatus = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/live/status`);
      const data = await response.json();
      
      if (data) {
        setLiveStatus({
          is_live: data.is_live || false,
          current_viewers: data.current_viewers || '0',
          live_game: data.live_game || 'FORTNITE'
        });
        
        // Update dashboard stats if needed
        setDashboardStats(prev => ({
          ...prev,
          channel_stats: {
            ...prev.channel_stats,
            is_live: data.is_live,
            current_viewers: data.current_viewers
          }
        }));
      }
    } catch (error) {
      console.warn('Live status check failed:', error);
    }
  };

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load real-time stats (includes YouTube sync)
      const stats = await apiCall('/api/admin/dashboard/real-time-stats');
      setDashboardStats(stats);
      
      if (stats && stats.channel_stats) {
        setLiveStatus({
          is_live: stats.channel_stats.is_live || false,
          current_viewers: stats.channel_stats.current_viewers || '0',
          live_game: stats.channel_stats.live_game || 'FORTNITE'
        });
        
        setChannelStats({
          subscriber_count: stats.channel_stats.subscriber_count || '0',
          video_count: stats.channel_stats.video_count || '0',
          total_views: stats.channel_stats.view_count || stats.channel_stats.total_views || '0'
        });
      } else {
        // Set default values if no channel stats
        setChannelStats({
          subscriber_count: '0',
          video_count: '0',
          total_views: '0'
        });
      }

      // Load YouTube sync status
      try {
        const syncStatus = await apiCall('/api/admin/youtube/sync-status');
        setYoutubeSync(syncStatus);
      } catch (syncError) {
        console.warn('YouTube sync status not available:', syncError);
      }

      // Load YouTube channel stats directly
      try {
        const youtubeStats = await apiCall('/api/youtube/channel-stats');
        if (youtubeStats) {
          setChannelStats({
            subscriber_count: youtubeStats.subscriber_count || '0',
            video_count: youtubeStats.video_count || '0',
            total_views: youtubeStats.view_count || '0'
          });
          console.log('✅ YouTube stats loaded:', youtubeStats);
        }
      } catch (youtubeError) {
        console.warn('YouTube channel stats not available:', youtubeError);
      }

      // Load schedule
      try {
        const schedule = await apiCall('/api/admin/schedule');
        setStreamSchedule(schedule || []);
      } catch (scheduleError) {
        console.warn('Schedule not available:', scheduleError);
      }

      // Load about content
      try {
        const about = await apiCall('/api/admin/content/about');
        if (about && about.content) {
          setAboutContent(about.content);
        }
      } catch (aboutError) {
        console.warn('About content not available:', aboutError);
      }
      
      // Load about tags
      try {
        const tagsData = await apiCall('/api/admin/content/tags');
        if (tagsData && tagsData.tags) {
          setAboutTags(tagsData.tags);
        }
      } catch (tagsError) {
        console.warn('About tags not available:', tagsError);
      }

      // Load featured video
      try {
        const featuredData = await apiCall('/api/admin/content/featured-video');
        if (featuredData) {
          setSiteContent(prev => ({
            ...prev,
            featured_video: featuredData
          }));
        }
      } catch (featuredError) {
        console.warn('Featured video not available:', featuredError);
      }

      // Load polls and predictions
      loadPolls();
      loadPredictions();
      
    } catch (error) {
      console.error('Dashboard load error:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  // Toggle live status
  const toggleLiveStatus = async () => {
    try {
      const newStatus = !liveStatus.is_live;
      const response = await apiCall('/api/admin/live/toggle', 'POST', {
        is_live: newStatus,
        current_viewers: liveStatus.current_viewers,
        live_game: liveStatus.live_game
      });

      if (response.success) {
        setLiveStatus(prev => ({ ...prev, is_live: newStatus }));
      }
    } catch (error) {
      console.error('Toggle live error:', error);
    }
  };

  // Update channel stats
  const updateChannelStats = async () => {
    try {
      const response = await apiCall('/api/admin/stats/update', 'POST', channelStats);
      if (response.success) {
        alert('Channel stats updated successfully!');
      }
    } catch (error) {
      console.error('Update stats error:', error);
    }
  };

  // Refresh YouTube stats
  const refreshYoutubeStats = async () => {
    try {
      setLoading(true);
      const youtubeStats = await apiCall('/api/youtube/channel-stats');
      if (youtubeStats) {
        setChannelStats({
          subscriber_count: youtubeStats.subscriber_count || '0',
          video_count: youtubeStats.video_count || '0',
          total_views: youtubeStats.view_count || '0'
        });
        alert('✅ YouTube stats refreshed successfully!');
      }
    } catch (error) {
      console.error('YouTube stats refresh error:', error);
      alert('❌ Failed to refresh YouTube stats');
    } finally {
      setLoading(false);
    }
  };

  // Manual YouTube sync
  const triggerYoutubeSync = async () => {
    try {
      setLoading(true);
      const response = await apiCall('/api/admin/youtube/sync', 'POST');
      
      if (response.success) {
        alert('✅ YouTube sync completed successfully!');
        await loadDashboardData(); // Refresh data
      } else {
        alert(`❌ YouTube sync failed: ${response.message}`);
      }
    } catch (error) {
      console.error('Manual sync error:', error);
      alert('❌ YouTube sync failed');
    } finally {
      setLoading(false);
    }
  };

  // Add new schedule entry
  const addScheduleEntry = async () => {
    try {
      const response = await apiCall('/api/admin/schedule/update', 'POST', newSchedule);
      if (response.success) {
        alert('✅ Schedule updated successfully!');
        setNewSchedule({ day: 'MON', time: '19:00', game: 'FORTNITE' });
        loadDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Add schedule error:', error);
      alert('❌ Schedule update failed');
    }
  };

  // Update about content
  const updateAboutContent = async () => {
    try {
      const response = await apiCall('/api/admin/content/about/update', 'POST', {
        content: aboutContent
      });
      if (response.success) {
        alert('✅ About content updated successfully!');
      }
    } catch (error) {
      console.error('About update error:', error);
      alert('❌ About content update failed');
    }
  };
  
  // Update about tags
  const updateAboutTags = async () => {
    try {
      const response = await apiCall('/api/admin/content/tags/update', 'POST', {
        tags: aboutTags
      });
      if (response.success) {
        alert('✅ About tags updated successfully!');
      }
    } catch (error) {
      console.error('Tags update error:', error);
      alert('❌ Tags update failed');
    }
  };

  // Schedule Management Functions
  const updateSchedule = async () => {
    try {
      const response = await apiCall('/api/admin/schedule/update', 'POST', newSchedule);
      if (response.success) {
        alert('✅ Schedule updated successfully! Homepage will update instantly.');
        // Update local state
        const updatedSchedule = response.schedule || [];
        setStreamSchedule(updatedSchedule);
        // Reset form
        setNewSchedule({ day: 'MON', time: '19:00', game: 'FORTNITE' });
      }
    } catch (error) {
      console.error('Update schedule error:', error);
      alert('❌ Failed to update schedule');
    }
  };

  const deleteSchedule = async (day) => {
    if (!confirm(`Delete schedule for ${day}?`)) return;
    
    try {
      const response = await apiCall(`/api/admin/schedule/${day}`, 'DELETE');
      if (response.success) {
        alert('✅ Schedule deleted! Homepage updated instantly.');
        // Update local state
        const updatedSchedule = response.schedule || [];
        setStreamSchedule(updatedSchedule);
      }
    } catch (error) {
      console.error('Delete schedule error:', error);
      alert('❌ Failed to delete schedule');
    }
  };

  // Theme Management Functions
  const loadThemes = async () => {
    try {
      // Use direct fetch for public endpoint
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/themes/list`);
      const data = await response.json();
      
      if (data.success && data.themes) {
        // Update available themes with backend data (includes more themes)
        setAvailableThemes(data.themes);
      }
      // Themes are already initialized with default values, so no action needed if API fails
    } catch (error) {
      console.error('Load themes error:', error);
      // Themes already initialized with default values in useState
    }
  };

  const loadCurrentTheme = async () => {
    try {
      // Use direct fetch for public endpoint
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/themes/current`);
      const data = await response.json();
      
      if (data.success && data.theme) {
        setCurrentTheme(data.theme);
        setSelectedTheme(data.theme.id || 'matrix_green');
      }
    } catch (error) {
      console.error('Load current theme error:', error);
    }
  };

  const applyTheme = async () => {
    try {
      // Use apiCall with authentication
      const data = await apiCall('/api/themes/apply', 'POST', {
        themeId: selectedTheme
      });
      
      if (data.success) {
        alert('✅ Theme applied! Homepage will reload with new theme.');
        await loadCurrentTheme();
        
        // Reload homepage to show new theme
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      } else {
        alert('❌ Failed to apply theme: ' + (data.detail || 'Unknown error'));
      }
    } catch (error) {
      console.error('Apply theme error:', error);
      alert('❌ Failed to apply theme: ' + error.message);
    }
  };

  // Polls Management
  const createPoll = async () => {
    try {
      const response = await apiCall('/api/polls/create', 'POST', newPoll);
      if (response.success) {
        alert('✅ Poll created successfully!');
        setNewPoll({ question: '', options: ['', ''] });
        loadPolls();
      }
    } catch (error) {
      console.error('Create poll error:', error);
      alert('❌ Failed to create poll');
    }
  };

  const loadPolls = async () => {
    try {
      const response = await apiCall('/api/polls/active', 'GET');
      setPolls(response.polls || []);
    } catch (error) {
      console.error('Load polls error:', error);
    }
  };

  const endPoll = async (pollId) => {
    try {
      const response = await apiCall(`/api/polls/end/${pollId}`, 'POST', {});
      if (response.success) {
        alert('✅ Poll ended!');
        loadPolls();
      }
    } catch (error) {
      console.error('End poll error:', error);
      alert('❌ Failed to end poll');
    }
  };

  const deletePoll = async (pollId) => {
    try {
      if (window.confirm('Delete this poll?')) {
        const response = await apiCall(`/api/polls/${pollId}`, 'DELETE');
        if (response.success) {
          alert('✅ Poll deleted!');
          loadPolls();
        }
      }
    } catch (error) {
      console.error('Delete poll error:', error);
      alert('❌ Failed to delete poll');
    }
  };

  // Predictions Management
  const createPrediction = async () => {
    try {
      const response = await apiCall('/api/predictions/create', 'POST', newPrediction);
      if (response.success) {
        alert('✅ Prediction created successfully!');
        setNewPrediction({ question: '', option_a: '', option_b: '' });
        loadPredictions();
      }
    } catch (error) {
      console.error('Create prediction error:', error);
      alert('❌ Failed to create prediction');
    }
  };

  const loadPredictions = async () => {
    try {
      const response = await apiCall('/api/predictions/active', 'GET');
      setPredictions(response.predictions || []);
    } catch (error) {
      console.error('Load predictions error:', error);
    }
  };

  const resolvePrediction = async (predictionId, result) => {
    try {
      const response = await apiCall(`/api/predictions/resolve/${predictionId}`, 'POST', { result });
      if (response.success) {
        alert(`✅ Prediction resolved! Accuracy: ${response.accuracy}%`);
        loadPredictions();
      }
    } catch (error) {
      console.error('Resolve prediction error:', error);
      alert('❌ Failed to resolve prediction');
    }
  };

  const deletePrediction = async (predictionId) => {
    try {
      if (window.confirm('Delete this prediction?')) {
        const response = await apiCall(`/api/predictions/${predictionId}`, 'DELETE');
        if (response.success) {
          alert('✅ Prediction deleted!');
          loadPredictions();
        }
      }
    } catch (error) {
      console.error('Delete prediction error:', error);
      alert('❌ Failed to delete prediction');
    }
  };

  // Delete schedule entry  
  const deleteScheduleEntry = async (day) => {
    try {
      if (window.confirm(`Delete schedule for ${day}?`)) {
        const response = await apiCall(`/api/admin/schedule/${day}`, 'DELETE');
        if (response.success) {
          alert('✅ Schedule deleted successfully!');
          loadDashboardData();
        }
      }
    } catch (error) {
      console.error('Delete schedule error:', error);
      alert('❌ Schedule delete failed');
    }
  };
  const updateSiteContent = async (contentType, data) => {
    try {
      let endpoint;
      switch (contentType) {
        case 'about':
          endpoint = '/api/admin/content/about/update';
          break;
        case 'featured_video':
          endpoint = '/api/admin/content/featured-video/update';
          break;
        default:
          throw new Error('Invalid content type');
      }
      
      const response = await apiCall(endpoint, 'POST', data);
      if (response.success) {
        alert('✅ Site content updated successfully!');
        loadDashboardData();
      }
    } catch (error) {
      console.error('Content update error:', error);
      alert('❌ Content update failed');
    }
  };
  const addNewStream = async () => {
    try {
      if (!newStream.title || !newStream.game || !newStream.video_url) {
        alert('Please fill all required fields');
        return;
      }

      const response = await apiCall('/api/admin/streams/add', 'POST', newStream);
      if (response.success) {
        alert('Stream added successfully!');
        setNewStream({ title: '', game: '', duration: '', views: '', video_url: '' });
        loadDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Add stream error:', error);
    }
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      await apiCall('/api/admin/auth/logout', 'POST');
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_id');
      onLogout();
    } catch (error) {
      console.error('Logout error:', error);
      onLogout(); // Force logout even if API fails
    }
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="loading-spinner-large"></div>
        <p>Loading Admin Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      {/* Header */}
      <motion.header 
        className="admin-header"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <div className="admin-header-content">
          <div className="admin-logo">
            <h1>🎮 {t('adminTitle')}</h1>
            <span className="admin-subtitle">{t('gamingDashboard')}</span>
          </div>
          
          <div className="admin-actions">
            <div className="live-status-display">
              <div className={`live-indicator ${liveStatus.is_live ? 'live' : 'offline'}`}>
                {liveStatus.is_live ? `🔴 ${t('liveNow')}` : `⚫ ${t('offline')}`}
              </div>
              {liveStatus.is_live && (
                <span className="viewer-count">{liveStatus.current_viewers} {t('viewers')}</span>
              )}
            </div>
            
            <motion.button
              className="logout-button"
              onClick={handleLogout}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              🚪 {t('logout')}
            </motion.button>
          </div>
        </div>
      </motion.header>

      {/* Navigation Tabs */}
      <motion.nav 
        className="admin-nav"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        {[
          { id: 'overview', label: t('overview'), icon: '📊' },
          { id: 'settings', label: 'SITE SETTINGS', icon: '⚙️' },
          { id: 'youtube', label: t('youtubeSync'), icon: '🎥' },
          { id: 'obs', label: 'OBS CONTROL', icon: '🎬' },
          { id: 'streamlabs', label: 'STREAMLABS', icon: '💰' },
          { id: 'live', label: t('liveControl'), icon: '🔴' },
          { id: 'content', label: t('content'), icon: '📹' },
          { id: 'site', label: t('siteControl'), icon: '🌐' },
          { id: 'schedule', label: t('schedule'), icon: '📅' },
          { id: 'customization', label: 'CUSTOMIZATION', icon: '🎨' },
          { id: 'viewer-system', label: 'VIEWER SYSTEM', icon: '🎮' },
          { id: 'engagement', label: 'ENGAGEMENT', icon: '🎯' },
          { id: 'stats', label: t('stats'), icon: '📈' }
        ].map((tab) => (
          <motion.button
            key={tab.id}
            className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </motion.button>
        ))}
      </motion.nav>

      {/* Main Content */}
      <motion.main 
        className="admin-main"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        {activeTab === 'youtube' && (
          <div className="youtube-section">
            <h2>🎥 {t('youtubeIntegration')}</h2>
            
            <div className="sync-controls">
              <div className="sync-status-card">
                <h3>🔄 {t('syncNow')}</h3>
                
                <div className="sync-info">
                  <div className="info-item">
                    <span className="info-label">Status:</span>
                    <span className={`info-value ${youtubeSync.sync_active ? 'active' : 'inactive'}`}>
                      {youtubeSync.sync_active ? '🟢 Active' : '🔴 Inactive'}
                    </span>
                  </div>
                  
                  <div className="info-item">
                    <span className="info-label">{t('lastSync')}:</span>
                    <span className="info-value">
                      {youtubeSync.last_sync ? new Date(youtubeSync.last_sync).toLocaleString() : 'Never'}
                    </span>
                  </div>
                  
                  <div className="info-item">
                    <span className="info-label">Next Sync:</span>
                    <span className="info-value">{youtubeSync.next_sync || 'Every 5 minutes'}</span>
                  </div>
                </div>
                
                <button 
                  className="sync-button"
                  onClick={refreshYoutubeStats}
                  disabled={loading}
                >
                  🔄 Refresh Stats
                </button>
              </div>

              <div className="current-data-card">
                <h3>📊 {t('channelStats')}</h3>
                
                <div className="data-grid">
                  <div className="data-item">
                    <span className="data-label">{t('subscribers')}:</span>
                    <span className="data-value">{channelStats.subscriber_count}</span>
                  </div>
                  
                  <div className="data-item">
                    <span className="data-label">{t('totalVideos')}:</span>
                    <span className="data-value">{channelStats.video_count}</span>
                  </div>
                  
                  <div className="data-item">
                    <span className="data-label">{t('totalViews')}:</span>
                    <span className="data-value">{channelStats.total_views}</span>
                  </div>
                  
                  <div className="data-item">
                    <span className="data-label">{t('currentStatus')}:</span>
                    <span className={`data-value ${liveStatus.is_live ? 'live' : 'offline'}`}>
                      {liveStatus.is_live ? `🔴 ${t('liveNow')} (${liveStatus.current_viewers} ${t('viewers')})` : `⚫ ${t('offline')}`}
                    </span>
                  </div>
                </div>
                
                <div className="sync-features">
                  <h4>🎯 {t('autoSync')}</h4>
                  <ul>
                    <li>✅ {t('subscribers')} updates</li>
                    <li>✅ {t('liveNow')} detection</li>
                    <li>✅ {t('totalVideos')} notifications</li>
                    <li>✅ {t('viewerCount')} tracking</li>
                    <li>✅ {t('channelStats')} sync</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'obs' && (
          <AdminOBSPanel token={token} />
        )}

        {activeTab === 'streamlabs' && (
          <AdminStreamlabsPanel token={token} />
        )}

        {activeTab === 'site' && (
          <div className="site-section">
            <h2>🌐 {t('completeSiteControl')}</h2>
            
            <div className="site-controls">
              <div className="content-editor-card">
                <h3>✏️ {t('aboutSection')}</h3>
                
                <div className="editor-content">
                  <p>{t('editAboutDesc')}</p>
                  
                  {aboutContent.map((line, index) => (
                    <div key={index} className="about-line-editor">
                      <textarea
                        value={line}
                        onChange={(e) => {
                          const newContent = [...aboutContent];
                          newContent[index] = e.target.value;
                          setAboutContent(newContent);
                        }}
                        rows="2"
                        className="content-textarea"
                        placeholder={`Line ${index + 1}...`}
                      />
                      <button 
                        className="remove-line-btn"
                        onClick={() => {
                          const newContent = aboutContent.filter((_, i) => i !== index);
                          setAboutContent(newContent);
                        }}
                      >
                        ❌
                      </button>
                    </div>
                  ))}
                  
                  <button 
                    className="add-line-btn"
                    onClick={() => setAboutContent([...aboutContent, ""])}
                  >
                    ➕ {t('addNewLine')}
                  </button>
                  
                  <button 
                    className="update-content-btn"
                    onClick={updateAboutContent}
                  >
                    💾 {t('updateAbout')}
                  </button>
                </div>
              </div>

              <div className="content-editor-card">
                <h3>🏷️ About Tags</h3>
                
                <div className="editor-content">
                  <p>Manage the tags/badges displayed below About section</p>
                  
                  {aboutTags.map((tag, index) => (
                    <div key={index} className="about-line-editor">
                      <input
                        type="text"
                        value={tag.icon}
                        onChange={(e) => {
                          const newTags = [...aboutTags];
                          newTags[index].icon = e.target.value;
                          setAboutTags(newTags);
                        }}
                        placeholder="🏆"
                        style={{ width: '60px', marginRight: '10px' }}
                        className="content-textarea"
                      />
                      <input
                        type="text"
                        value={tag.text}
                        onChange={(e) => {
                          const newTags = [...aboutTags];
                          newTags[index].text = e.target.value;
                          setAboutTags(newTags);
                        }}
                        placeholder="Tag text"
                        style={{ flex: 1 }}
                        className="content-textarea"
                      />
                      <button 
                        className="remove-line-btn"
                        onClick={() => {
                          const newTags = aboutTags.filter((_, i) => i !== index);
                          setAboutTags(newTags);
                        }}
                      >
                        ❌
                      </button>
                    </div>
                  ))}
                  
                  <button 
                    className="add-line-btn"
                    onClick={() => setAboutTags([...aboutTags, { icon: "🎮", text: "" }])}
                  >
                    ➕ {t('addNewTag') || 'Add New Tag'}
                  </button>
                  
                  <button 
                    className="update-content-btn"
                    onClick={updateAboutTags}
                  >
                    💾 {t('updateTags') || 'Update Tags'}
                  </button>
                </div>
              </div>

              <div className="featured-video-card">
                <h3>🎬 {t('featuredVideo')}</h3>
                
                <div className="video-controls">
                  <div className="input-group">
                    <label>{t('videoId')}</label>
                    <input
                      type="text"
                      placeholder="e.g. GUhc9NBBxBM"
                      value={siteContent.featured_video?.video_id || ''}
                      onChange={(e) => setSiteContent({
                        ...siteContent,
                        featured_video: { ...siteContent.featured_video, video_id: e.target.value }
                      })}
                    />
                  </div>
                  
                  <div className="input-group">
                    <label>{t('videoTitle')}</label>
                    <input
                      type="text"
                      placeholder="REMZA019 - Video Title"
                      value={siteContent.featured_video?.title || ''}
                      onChange={(e) => setSiteContent({
                        ...siteContent,
                        featured_video: { ...siteContent.featured_video, title: e.target.value }
                      })}
                    />
                  </div>
                  
                  <div className="input-group">
                    <label>{t('videoDescription')}</label>
                    <textarea
                      rows="3"
                      placeholder={t('videoDescription')}
                      value={siteContent.featured_video?.description || ''}
                      onChange={(e) => setSiteContent({
                        ...siteContent,
                        featured_video: { ...siteContent.featured_video, description: e.target.value }
                      })}
                    />
                  </div>
                  
                  <button 
                    className="update-featured-btn"
                    onClick={() => updateSiteContent('featured_video', siteContent.featured_video)}
                  >
                    🎬 {t('updateFeaturedVideo')}
                  </button>
                </div>
              </div>

              <div className="live-preview-card">
                <h3>👁️ {t('livePreview')}</h3>
                
                <div className="preview-info">
                  <p>🔄 {t('allChangesUpdate')}</p>
                  <p>🌐 {t('previewChanges')} <a href="/" target="_blank">{t('gamingSite')}</a></p>
                </div>
                
                <div className="preview-actions">
                  <button 
                    className="preview-btn"
                    onClick={() => window.open('/', '_blank')}
                  >
                    🔍 {t('gamingSite')}
                  </button>
                  <button 
                    className="refresh-btn"
                    onClick={loadDashboardData}
                  >
                    🔄 {t('refreshData')}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'overview' && (
          <div className="overview-section">
            <h2>📊 Dashboard Overview</h2>
            
            {dashboardStats && dashboardStats.channel_stats && (
              <div className="stats-grid">
                <div className="stat-card">
                  <h3>👥 {t('subscribers')}</h3>
                  <p className="stat-number">{dashboardStats.channel_stats.subscriber_count || '0'}</p>
                </div>
                <div className="stat-card">
                  <h3>📹 {t('totalVideos')}</h3>
                  <p className="stat-number">{dashboardStats.channel_stats.video_count || '0'}</p>
                </div>
                <div className="stat-card">
                  <h3>👀 {t('totalViews')}</h3>
                  <p className="stat-number">{dashboardStats.channel_stats.total_views || dashboardStats.channel_stats.view_count || '0'}</p>
                </div>
                <div className="stat-card">
                  <h3>🎮 {t('recentStreams')}</h3>
                  <p className="stat-number">{dashboardStats.recent_streams_count}</p>
                </div>
              </div>
            )}

            <div className="quick-actions">
              <h3>⚡ {t('quickActions')}</h3>
              <div className="action-buttons">
                <button 
                  className="quick-action-btn live-toggle"
                  onClick={toggleLiveStatus}
                >
                  {liveStatus.is_live ? `🔴 ${t('setOffline')}` : `🟢 ${t('goLive')}`}
                </button>
                <button 
                  className="quick-action-btn"
                  onClick={() => setActiveTab('content')}
                >
                  📹 {t('content')}
                </button>
                <button 
                  className="quick-action-btn"
                  onClick={() => setActiveTab('schedule')}
                >
                  📅 {t('updateSchedule')}
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'live' && (
          <div className="live-section">
            <h2>🔴 {t('liveStreamControl')}</h2>
            
            <div className="live-control-panel">
              <div className="live-status-card">
                <h3>{t('currentStatus')}</h3>
                <div className={`status-display ${liveStatus.is_live ? 'live' : 'offline'}`}>
                  {liveStatus.is_live ? `🔴 ${t('liveNow')}` : `⚫ ${t('offline')}`}
                </div>
                
                <button 
                  className={`live-toggle-btn ${liveStatus.is_live ? 'stop' : 'start'}`}
                  onClick={toggleLiveStatus}
                >
                  {liveStatus.is_live ? t('setOffline') : t('setLive')}
                </button>
              </div>

              <div className="live-details-card">
                <h3>{t('content')}</h3>
                
                <div className="input-group">
                  <label>{t('viewerCount')}</label>
                  <input
                    type="text"
                    value={liveStatus.current_viewers}
                    onChange={(e) => setLiveStatus({...liveStatus, current_viewers: e.target.value})}
                    placeholder="0"
                  />
                </div>

                <div className="input-group">
                  <label>{t('currentGame')}</label>
                  <input
                    type="text"
                    value={liveStatus.live_game}
                    onChange={(e) => setLiveStatus({...liveStatus, live_game: e.target.value})}
                    placeholder="e.g. FORTNITE"
                  />
                </div>

                <button 
                  className="update-btn"
                  onClick={() => apiCall('/api/admin/live/toggle', 'POST', liveStatus)}
                >
                  {t('updateStatus')}
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'content' && (
          <div className="content-section">
            <h2>📹 Content Management</h2>
            
            {/* About Content Management */}
            <div className="about-management-card">
              <h3>📝 About Section Content</h3>
              <div className="input-group">
                <label>About Text</label>
                <textarea
                  rows={3}
                  value={aboutText}
                  onChange={(e) => setAboutText(e.target.value)}
                  placeholder="Describe your channel..."
                />
              </div>
              <button className="save-about-btn" onClick={saveAboutContent}>💾 Save About Content</button>
            </div>
            
            {/* About Tags Management */}
            <div className="tags-management-card">
              <h3>🏷️ About Tags</h3>
              <div style={{marginBottom: '20px', padding: '15px', background: 'rgba(255,255,0,0.1)', border: '1px solid rgba(255,255,0,0.5)', borderRadius: '8px'}}>
                <p style={{marginBottom: '10px', color: '#ffff00', fontSize: '14px', fontWeight: 'bold'}}>
                  ⚠️ VAŽNO: Kako uneti tagove
                </p>
                <ul style={{margin: 0, marginBottom: '10px', paddingLeft: '20px', color: 'rgba(0,255,0,0.8)', fontSize: '13px'}}>
                  <li><strong>PRVO POLJE (usko):</strong> Samo EMOJI - npr: 🏆 ili 🎮</li>
                  <li><strong>DRUGO POLJE (široko):</strong> Tekst - npr: "Competitive Player"</li>
                </ul>
                <div style={{padding: '10px', background: 'rgba(0,0,0,0.3)', borderRadius: '5px', borderLeft: '3px solid #00ff00'}}>
                  <p style={{margin: 0, color: '#00ff00', fontSize: '12px', fontWeight: 'bold'}}>✅ PRIMER PRAVILNOG UNOSA:</p>
                  <p style={{margin: '5px 0', color: 'rgba(0,255,0,0.7)', fontSize: '11px'}}>
                    EMOJI: 🏆 | TEKST: Competitive Player → Rezultat: <span style={{color: '#00ff00'}}>🏆 Competitive Player</span>
                  </p>
                  <p style={{margin: 0, color: '#ff5555', fontSize: '12px', fontWeight: 'bold'}}>❌ PRIMER POGREŠNOG UNOSA:</p>
                  <p style={{margin: '5px 0', color: 'rgba(255,85,85,0.7)', fontSize: '11px'}}>
                    EMOJI: 🏆 Competitive | TEKST: Player → Rezultat: <span style={{color: '#ff5555'}}>🏆 Competitive Player</span> (duplikat teksta!)
                  </p>
                </div>
              </div>
              <div className="tags-list">
                {aboutTags.map((tag, idx) => (
                  <div key={idx} className="tag-edit-row">
                    <div style={{display: 'flex', flexDirection: 'column', width: '80px'}}>
                      <label style={{fontSize: '11px', color: 'rgba(0,255,0,0.6)', marginBottom: '3px'}}>EMOJI</label>
                      <input 
                        type="text" 
                        value={tag.icon}
                        onChange={(e) => updateTag(idx, 'icon', e.target.value)}
                        placeholder="🏆" 
                        style={{width: '70px', textAlign: 'center', fontSize: '20px'}}
                      />
                    </div>
                    <div style={{display: 'flex', flexDirection: 'column', flex: 1}}>
                      <label style={{fontSize: '11px', color: 'rgba(0,255,0,0.6)', marginBottom: '3px'}}>OPIS TAGA</label>
                      <input 
                        type="text" 
                        value={tag.text}
                        onChange={(e) => updateTag(idx, 'text', e.target.value)}
                        placeholder="npr: Competitive Player" 
                        style={{flex: 1}}
                      />
                    </div>
                  </div>
                ))}
              </div>
              <div style={{display: 'flex', gap: '10px', marginTop: '10px'}}>
                <button className="save-tags-btn" onClick={saveAboutTags}>💾 Save Tags</button>
                <button 
                  className="save-tags-btn" 
                  style={{background: 'rgba(255,255,0,0.2)', border: '1px solid #ffff00', color: '#ffff00'}}
                  onClick={() => {
                    const defaultTags = [
                      { icon: "🏆", text: "Competitive Player" },
                      { icon: "🏎️", text: "Rocket Racing Specialist" },
                      { icon: "📺", text: "Content Creator" },
                      { icon: "🇷🇸", text: "Serbia (CET)" },
                      { icon: "💯", text: "Authentic Gameplay" }
                    ];
                    if (window.confirm('Reset tags to default values?')) {
                      setAboutTags(defaultTags);
                      alert('Tags reset! Click "Save Tags" to apply.');
                    }
                  }}
                >
                  🔄 Reset to Default
                </button>
              </div>
            </div>
            
            <div className="add-stream-card">
              <h3>Add New Stream/Video</h3>
              
              <div className="form-grid">
                <div className="input-group">
                  <label>Title *</label>
                  <input
                    type="text"
                    value={newStream.title}
                    onChange={(e) => setNewStream({...newStream, title: e.target.value})}
                    placeholder="e.g. REMZA019 - Competitive Racing"
                  />
                </div>

                <div className="input-group">
                  <label>Game *</label>
                  <input
                    type="text"
                    value={newStream.game}
                    onChange={(e) => setNewStream({...newStream, game: e.target.value})}
                    placeholder="e.g. FORTNITE ROCKET RACING"
                  />
                </div>

                <div className="input-group">
                  <label>Duration</label>
                  <input
                    type="text"
                    value={newStream.duration}
                    onChange={(e) => setNewStream({...newStream, duration: e.target.value})}
                    placeholder="e.g. 2h 45m"
                  />
                </div>

                <div className="input-group">
                  <label>Views</label>
                  <input
                    type="text"
                    value={newStream.views}
                    onChange={(e) => setNewStream({...newStream, views: e.target.value})}
                    placeholder="e.g. 3.2K"
                  />
                </div>

                <div className="input-group full-width">
                  <label>YouTube URL *</label>
                  <input
                    type="url"
                    value={newStream.video_url}
                    onChange={(e) => setNewStream({...newStream, video_url: e.target.value})}
                    placeholder="https://www.youtube.com/watch?v=VIDEO_ID"
                  />
                </div>
              </div>

              <button 
                className="add-stream-btn"
                onClick={addNewStream}
              >
                ✅ Add Stream/Video
              </button>
            </div>
          </div>
        )}

        {activeTab === 'schedule' && (
          <div className="schedule-section">
            <h2>📅 {t('streamSchedule')}</h2>
            
            <div className="schedule-management">
              <div className="add-schedule-card">
                <h3>➕ {t('addSchedule')}</h3>
                
                <div className="schedule-form">
                  <div className="input-group">
                    <label>{t('day')}</label>
                    <select
                      value={newSchedule.day}
                      onChange={(e) => setNewSchedule({...newSchedule, day: e.target.value})}
                    >
                      <option value="MON">Monday</option>
                      <option value="TUE">Tuesday</option>
                      <option value="WED">Wednesday</option>
                      <option value="THU">Thursday</option>
                      <option value="FRI">Friday</option>
                      <option value="SAT">Saturday</option>
                      <option value="SUN">Sunday</option>
                    </select>
                  </div>
                  
                  <div className="input-group">
                    <label>{t('time')}</label>
                    <input
                      type="time"
                      value={newSchedule.time}
                      onChange={(e) => setNewSchedule({...newSchedule, time: e.target.value})}
                    />
                  </div>
                  
                  <div className="input-group">
                    <label>{t('game')}</label>
                    <select
                      value={newSchedule.game}
                      onChange={(e) => setNewSchedule({...newSchedule, game: e.target.value})}
                    >
                      <option value="FORTNITE">FORTNITE</option>
                      <option value="FORTNITE ROCKET RACING">FORTNITE ROCKET RACING</option>
                      <option value="COD MULTIPLAYER">COD MULTIPLAYER</option>
                      <option value="COD WARZONE">COD WARZONE</option>
                      <option value="FORTNITE TOURNAMENT">FORTNITE TOURNAMENT</option>
                    </select>
                  </div>
                  
                  <button 
                    className="add-schedule-btn"
                    onClick={addScheduleEntry}
                  >
                    ✅ {t('updateScheduleBtn')}
                  </button>
                </div>
              </div>

              <div className="current-schedule-card">
                <h3>📋 Current Schedule</h3>
                
                {streamSchedule.length > 0 ? (
                  <div className="schedule-list">
                    {streamSchedule.map((item, index) => (
                      <div key={index} className="schedule-item">
                        <div className="schedule-day">
                          <strong>{item.day}</strong>
                        </div>
                        <div className="schedule-time">
                          🕒 {item.time}
                        </div>
                        <div className="schedule-game">
                          🎮 {item.game}
                        </div>
                        <button 
                          className="delete-schedule-btn"
                          onClick={() => deleteScheduleEntry(item.day)}
                        >
                          🗑️
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="no-schedule">
                    <p>No schedule set. Add your first stream schedule above.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'stats' && (
          <div className="stats-section">
            <h2>📈 {t('channelStats')}</h2>
            
            <div className="stats-update-card">
              <h3>{t('statistics')}</h3>
              
              <div className="form-grid">
                <div className="input-group">
                  <label>{t('subscribers')}</label>
                  <input
                    type="text"
                    value={channelStats.subscriber_count}
                    onChange={(e) => setChannelStats({...channelStats, subscriber_count: e.target.value})}
                    placeholder="178"
                  />
                </div>

                <div className="input-group">
                  <label>{t('totalVideos')}</label>
                  <input
                    type="text"
                    value={channelStats.video_count}
                    onChange={(e) => setChannelStats({...channelStats, video_count: e.target.value})}
                    placeholder="15"
                  />
                </div>

                <div className="input-group">
                  <label>{t('totalViews')}</label>
                  <input
                    type="text"
                    value={channelStats.total_views}
                    onChange={(e) => setChannelStats({...channelStats, total_views: e.target.value})}
                    placeholder="3247"
                  />
                </div>
              </div>

              <button 
                className="update-stats-btn"
                onClick={updateChannelStats}
              >
                📈 {t('statistics')}
              </button>
            </div>
          </div>
        )}

        {/* Engagement Tab - Polls & Predictions */}
        {activeTab === 'engagement' && (
          <div className="engagement-tab">
            
            {/* Polls Section */}
            <div className="engagement-section">
              <h2>🗳️ POLLS MANAGEMENT</h2>
              
              <div className="create-poll-card">
                <h3>Create New Poll</h3>
                <input
                  type="text"
                  placeholder="Poll question..."
                  value={newPoll.question}
                  onChange={(e) => setNewPoll({...newPoll, question: e.target.value})}
                  className="poll-input"
                />
                
                {newPoll.options.map((option, idx) => (
                  <div key={idx} className="poll-option-input">
                    <input
                      type="text"
                      placeholder={`Option ${idx + 1}...`}
                      value={option}
                      onChange={(e) => {
                        const newOptions = [...newPoll.options];
                        newOptions[idx] = e.target.value;
                        setNewPoll({...newPoll, options: newOptions});
                      }}
                      className="poll-input"
                    />
                    {newPoll.options.length > 2 && (
                      <button 
                        onClick={() => {
                          const newOptions = newPoll.options.filter((_, i) => i !== idx);
                          setNewPoll({...newPoll, options: newOptions});
                        }}
                        className="remove-option-btn"
                      >
                        ❌
                      </button>
                    )}
                  </div>
                ))}
                
                <button 
                  onClick={() => setNewPoll({...newPoll, options: [...newPoll.options, '']})}
                  className="add-option-btn"
                >
                  ➕ Add Option
                </button>
                
                <button onClick={createPoll} className="create-poll-btn">
                  🗳️ Create Poll
                </button>
              </div>

              <div className="active-polls-list">
                <h3>Active Polls ({polls.length})</h3>
                {polls.map(poll => (
                  <div key={poll.id} className="poll-card">
                    <div className="poll-header">
                      <h4>{poll.question}</h4>
                      <span className="poll-votes">{poll.total_votes} votes</span>
                    </div>
                    
                    <div className="poll-options">
                      {poll.options.map(option => (
                        <div key={option.id} className="poll-option">
                          <span>{option.text}</span>
                          <span className="option-votes">{option.votes} votes</span>
                        </div>
                      ))}
                    </div>
                    
                    <div className="poll-actions">
                      <button onClick={() => endPoll(poll.id)} className="end-poll-btn">
                        ⏸️ End Poll
                      </button>
                      <button onClick={() => deletePoll(poll.id)} className="delete-poll-btn">
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Predictions Section */}
            <div className="engagement-section">
              <h2>🎯 PREDICTIONS MANAGEMENT</h2>
              
              <div className="create-prediction-card">
                <h3>Create New Prediction</h3>
                <input
                  type="text"
                  placeholder="Prediction question..."
                  value={newPrediction.question}
                  onChange={(e) => setNewPrediction({...newPrediction, question: e.target.value})}
                  className="poll-input"
                />
                
                <div className="prediction-options">
                  <input
                    type="text"
                    placeholder="Option A..."
                    value={newPrediction.option_a}
                    onChange={(e) => setNewPrediction({...newPrediction, option_a: e.target.value})}
                    className="poll-input"
                  />
                  <span className="vs-text">VS</span>
                  <input
                    type="text"
                    placeholder="Option B..."
                    value={newPrediction.option_b}
                    onChange={(e) => setNewPrediction({...newPrediction, option_b: e.target.value})}
                    className="poll-input"
                  />
                </div>
                
                <button onClick={createPrediction} className="create-poll-btn">
                  🎯 Create Prediction
                </button>
              </div>

              <div className="active-polls-list">
                <h3>Active Predictions ({predictions.length})</h3>
                {predictions.map(pred => (
                  <div key={pred.id} className="poll-card">
                    <div className="poll-header">
                      <h4>{pred.question}</h4>
                      <span className="poll-votes">{pred.total_votes} votes</span>
                    </div>
                    
                    <div className="prediction-display">
                      <div className="pred-option">
                        <span className="pred-label">A: {pred.option_a}</span>
                        {pred.result && <span>({pred.votes_a} votes)</span>}
                      </div>
                      <span className="vs-text">VS</span>
                      <div className="pred-option">
                        <span className="pred-label">B: {pred.option_b}</span>
                        {pred.result && <span>({pred.votes_b} votes)</span>}
                      </div>
                    </div>
                    
                    <div className="poll-actions">
                      {!pred.result && (
                        <>
                          <button 
                            onClick={() => resolvePrediction(pred.id, 'a')} 
                            className="resolve-btn"
                          >
                            ✅ A Wins
                          </button>
                          <button 
                            onClick={() => resolvePrediction(pred.id, 'b')} 
                            className="resolve-btn"
                          >
                            ✅ B Wins
                          </button>
                        </>
                      )}
                      {pred.result && (
                        <span className="resolved-text">
                          ✅ Resolved: Option {pred.result.toUpperCase()} won!
                        </span>
                      )}
                      <button onClick={() => deletePrediction(pred.id)} className="delete-poll-btn">
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Schedule Tab */}
        {activeTab === 'schedule' && (
          <div className="schedule-section">
            <h2>📅 STREAM SCHEDULE MANAGEMENT</h2>
            
            <div className="schedule-editor">
              <h3>Edit Weekly Schedule</h3>
              
              <div className="schedule-form">
                <select 
                  value={newSchedule.day} 
                  onChange={(e) => setNewSchedule({...newSchedule, day: e.target.value})}
                  className="schedule-select"
                >
                  <option value="MON">Monday</option>
                  <option value="TUE">Tuesday</option>
                  <option value="WED">Wednesday</option>
                  <option value="THU">Thursday</option>
                  <option value="FRI">Friday</option>
                  <option value="SAT">Saturday</option>
                  <option value="SUN">Sunday</option>
                </select>
                
                <input
                  type="time"
                  value={newSchedule.time}
                  onChange={(e) => setNewSchedule({...newSchedule, time: e.target.value})}
                  className="schedule-input"
                />
                
                <input
                  type="text"
                  placeholder="Game/Content (e.g., FORTNITE)"
                  value={newSchedule.game}
                  onChange={(e) => setNewSchedule({...newSchedule, game: e.target.value})}
                  className="schedule-input"
                />
                
                <button onClick={updateSchedule} className="update-schedule-btn">
                  ✅ Update Schedule
                </button>
              </div>
              
              <div className="current-schedule">
                <h3>Current Schedule</h3>
                <div className="schedule-grid">
                  {['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'].map(day => {
                    const daySchedule = streamSchedule.find(s => s.day === day);
                    return (
                      <div key={day} className="schedule-day-card">
                        <div className="day-header">{day}</div>
                        {daySchedule ? (
                          <div className="day-content">
                            <div className="day-time">🕐 {daySchedule.time}</div>
                            <div className="day-game">🎮 {daySchedule.game}</div>
                            <button 
                              onClick={() => deleteSchedule(day)} 
                              className="delete-day-btn"
                            >
                              🗑️ Delete
                            </button>
                          </div>
                        ) : (
                          <div className="day-content empty">
                            <div className="day-time">No stream</div>
                            <button 
                              onClick={() => setNewSchedule({...newSchedule, day: day})}
                              className="add-day-btn"
                            >
                              ➕ Add
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Customization Tab */}
        {activeTab === 'customization' && (
          <div className="customization-tab">
            <h2>🎨 SITE CUSTOMIZATION</h2>
            
            {/* Theme Switcher Section */}
            <div className="theme-switcher-section">
              <h3>Theme Selection</h3>
              <p>Choose a pre-configured theme for your gaming platform:</p>
              
              <div className="theme-grid">
                {availableThemes.map(theme => (
                  <div 
                    key={theme.id}
                    className={`theme-card ${selectedTheme === theme.id ? 'selected' : ''}`}
                    onClick={() => setSelectedTheme(theme.id)}
                  >
                    <div className="theme-preview" style={{
                      background: theme.preview.primary,
                      border: `2px solid ${theme.preview.accent}`
                    }}>
                      <div className="theme-preview-text" style={{ color: theme.preview.text }}>
                        Aa
                      </div>
                    </div>
                    <div className="theme-info">
                      <div className="theme-name">{theme.name}</div>
                      <div className="theme-description">{theme.description}</div>
                    </div>
                    {selectedTheme === theme.id && (
                      <div className="theme-selected-badge">✓ Selected</div>
                    )}
                  </div>
                ))}
              </div>
              
              <div className="theme-actions">
                <div className="current-theme-info">
                  <strong>Current Theme:</strong> {currentTheme?.name || 'Loading...'}
                </div>
                <button onClick={applyTheme} className="apply-theme-btn">
                  🎨 Apply Theme
                </button>
              </div>
            </div>

            <hr style={{ margin: '2rem 0', border: '1px solid rgba(255,255,255,0.1)' }} />

            {/* Advanced Customization */}
            <AdminCustomizationPanel />
          </div>
        )}

        {/* VIEWER SYSTEM TAB - New! */}
        {activeTab === 'viewer-system' && (
          <AdminViewerSystem />
        )}

        {/* SCHEDULE TAB - New! */}
        {activeTab === 'schedule' && (
          <AdminSchedulePanel />
        )}

        {/* SITE SETTINGS TAB - New! */}
        {activeTab === 'settings' && (
          <AdminSiteSettings />
        )}

      </motion.main>

      {error && (
        <div className="error-notification">
          ❌ {error}
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;