import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '../i18n/LanguageContext';
import MatrixRain from './MatrixRain';
import AdminPanelWrapper from './admin/AdminPanelWrapper';
import NotificationSubscription from './NotificationSubscription';
import ViewerMenu from './ViewerMenu';
import DonationModal from './DonationModal';
import Leaderboard from './Leaderboard';
import PollsWidget from './PollsWidget';
import PredictionsWidget from './PredictionsWidget';
import VersionChecker from './VersionChecker';
import Logo3D from './Logo3D';
import LanguageSwitcher from './LanguageSwitcher';
import TrialStatus from './TrialStatus';
import LicenseModal from './LicenseModal';
import LicenseActivation from './LicenseActivation';
import CustomizationModal from './CustomizationModal';
import SocialLinks from './SocialLinks';
import SocialLinksFooter from './SocialLinksFooter';
import ScheduleWidget from './ScheduleWidget';
import PointsTracker from './PointsTracker';
import { getCustomization, updateCustomization, initializeLicense, isTrialExpired, getLicenseStatus, activateLicense } from '../utils/licenseManager';
import './GamingDemo.css';

const GamingDemo = () => {
  const { t } = useLanguage();
  const [isLive, setIsLive] = useState(false);
  const [viewerCount, setViewerCount] = useState(0);
  const [followerCount, setFollowerCount] = useState(2100);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [showDonationModal, setShowDonationModal] = useState(false);
  const [aboutContent, setAboutContent] = useState("Loading...");
  const [currentUser, setCurrentUser] = useState(() => {
    // Load user from localStorage
    const saved = localStorage.getItem('viewer_user');
    return saved ? JSON.parse(saved) : null;
  }); // For polls/predictions and points system
  const [featuredVideo, setFeaturedVideo] = useState(null); // Featured video
  const [aboutTags, setAboutTags] = useState([]); // Load from backend, no hardcoded default!
  const [licenseType, setLicenseType] = useState('NONE'); // License type for watermark control
  
  // PWA Install State
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPWAButton, setShowPWAButton] = useState(false);
  
  // License Management State
  const [showLicenseModal, setShowLicenseModal] = useState(false);
  const [trialExpired, setTrialExpired] = useState(false);
  const [showCustomizationModal, setShowCustomizationModal] = useState(false);
  
  // Customization State
  const [customization, setCustomization] = useState({
    userName: '019 Solutions',
    matrixColor: '#00ff00',
    textColor: '#00ff00',
    logoUrl: '/remza-logo.png',
    enablePWAInstall: true,
    aboutSectionTitle: 'About 019 Solutions',
    pwaInstallTitle: '📱 Install 019 Solutions App',
    adminPanelTitle: '🎮 REMZA019 Admin Panel',
    copyrightText: '© 2025 019 Solutions. All rights reserved.',
    tagline: '🎮 Professional Gaming Content Creator',
    distributionMode: false,
    communityLinks: {
      discord: '',
      youtube: '',
      twitch: '',
      twitter: '',
      instagram: '',
      tiktok: ''
    }
  });

  // Apply Theme Dynamically to Entire Application
  const applyTheme = (themeData) => {
    console.log('🎨 Applying theme:', themeData);
    
    if (!themeData || !themeData.colors) {
      console.warn('⚠️ No theme data provided');
      return;
    }
    
    const { colors, fonts, effects } = themeData;
    
    // Helper function to convert hex to RGB
    const hexToRgb = (hex) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` : '0, 255, 0';
    };
    
    // Apply colors as CSS variables
    if (colors) {
      // Apply all theme-specific variables
      Object.entries(colors).forEach(([key, value]) => {
        const cssVarName = `--theme-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`;
        document.documentElement.style.setProperty(cssVarName, value);
      });
      
      // CRITICAL: Override legacy variables with theme colors (these take priority!)
      document.documentElement.style.setProperty('--matrix-color', colors.primary);
      document.documentElement.style.setProperty('--text-color', colors.text);
      document.documentElement.style.setProperty('--bg-color', colors.background);
      document.documentElement.style.setProperty('--accent-color', colors.accent);
      
      // Set RGB version for rgba() usage
      document.documentElement.style.setProperty('--theme-primary-rgb', hexToRgb(colors.primary));
      document.documentElement.style.setProperty('--theme-text-rgb', hexToRgb(colors.text));
      
      // Auto-contrast text on colored backgrounds
      const getContrastText = (bgColor) => {
        const rgb = hexToRgb(bgColor).split(',').map(n => parseInt(n.trim()));
        const brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000;
        return brightness > 128 ? '#000000' : '#ffffff';
      };
      document.documentElement.style.setProperty('--theme-contrast-text', getContrastText(colors.primary));
      
      console.log(`🎨 Theme CSS Variables Applied:`, {
        '--matrix-color': colors.primary,
        '--text-color': colors.text,
        '--theme-primary': colors.primary,
        '--theme-primary-rgb': hexToRgb(colors.primary),
        '--theme-background': colors.background
      });
    }
    
    // Apply fonts
    if (fonts) {
      Object.entries(fonts).forEach(([key, value]) => {
        const cssVarName = `--font-${key}`;
        document.documentElement.style.setProperty(cssVarName, value);
      });
    }
    
    // Store theme in localStorage for persistence
    localStorage.setItem('current_theme', JSON.stringify(themeData));
    
    // FORCE RE-RENDER: Add a small visual cue
    document.body.setAttribute('data-theme', themeData.name.toLowerCase().replace(/ /g, '-'));
    
    console.log('✅ Theme applied successfully!');
  };
  
  // Load Theme from Backend
  const loadThemeFromBackend = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/themes/current`);
      const result = await response.json();
      
      if (result.success && result.theme) {
        console.log('✅ Theme loaded from backend:', result.theme);
        applyTheme(result.theme);
      } else {
        console.log('ℹ️ No custom theme, using default');
      }
    } catch (error) {
      console.error('❌ Failed to load theme from backend:', error);
      
      // Try to load from localStorage
      const savedTheme = localStorage.getItem('current_theme');
      if (savedTheme) {
        try {
          const themeData = JSON.parse(savedTheme);
          console.log('✅ Theme loaded from localStorage:', themeData);
          applyTheme(themeData);
        } catch (e) {
          console.error('❌ Failed to parse saved theme:', e);
        }
      }
    }
  };

  // Load Customization from Backend
  const loadCustomizationFromBackend = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/customization/current`);
      const result = await response.json();
      
      if (result.success && result.data) {
        console.log('✅ Customization loaded from backend:', result.data);
        
        // Transform social links to communityLinks format
        const communityLinks = {
          discord: result.data.discordLink || '',
          youtube: result.data.youtubeLink || '',
          twitch: result.data.twitchLink || '',
          twitter: result.data.twitterLink || '',
          instagram: result.data.instagramLink || '',
          tiktok: result.data.tiktokLink || ''
        };
        
        setCustomization({
          ...result.data,
          communityLinks
        });
        
        // Check if custom theme is active before applying customization colors
        const savedTheme = localStorage.getItem('current_theme');
        let hasCustomTheme = false;
        
        if (savedTheme) {
          try {
            const themeData = JSON.parse(savedTheme);
            hasCustomTheme = themeData.name && !themeData.name.includes('Matrix Green');
          } catch (e) {
            // If parse fails, no custom theme
            hasCustomTheme = false;
          }
        }
        
        // Only apply customization colors if NO custom theme is active
        if (!hasCustomTheme) {
          document.documentElement.style.setProperty('--matrix-color', result.data.matrixColor);
          document.documentElement.style.setProperty('--text-color', result.data.textColor);
        }
        
        // Always save to localStorage as cache (for other settings like logo, links)
        updateCustomization(result.data);
      }
    } catch (error) {
      console.error('Failed to load customization from backend:', error);
      
      // Fallback to localStorage
      const savedCustomization = getCustomization();
      setCustomization(savedCustomization);
      
      if (savedCustomization) {
        // Check for custom theme here too
        const savedTheme = localStorage.getItem('current_theme');
        let hasCustomTheme = false;
        
        if (savedTheme) {
          try {
            const themeData = JSON.parse(savedTheme);
            hasCustomTheme = themeData.name && !themeData.name.includes('Matrix Green');
          } catch (e) {
            hasCustomTheme = false;
          }
        }
        
        if (!hasCustomTheme) {
          document.documentElement.style.setProperty('--matrix-color', savedCustomization.matrixColor);
          document.documentElement.style.setProperty('--text-color', savedCustomization.textColor);
        }
      }
    }
  };
  
  // Load License Status
  const loadLicenseStatus = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/license/status`);
      const data = await response.json();
      
      if (data.is_active && data.license_type) {
        setLicenseType(data.license_type);
        console.log('🔑 License Type:', data.license_type);
      } else {
        setLicenseType('NONE');
        console.log('🔑 No active license - showing watermark');
      }
    } catch (error) {
      console.error('Failed to load license status:', error);
      setLicenseType('NONE');
    }
  };
  
  // Handle points update from PointsTracker
  const handlePointsUpdate = (updateData) => {
    setCurrentUser(prev => {
      const updated = {
        ...prev,
        points: updateData.points,
        level: updateData.level,
        levelName: updateData.levelName
      };
      localStorage.setItem('viewer_user', JSON.stringify(updated));
      return updated;
    });
  };

  // License Initialization - CHECK ON MOUNT
  useEffect(() => {
    // Initialize license on first visit
    initializeLicense();
    
    // Load license status
    loadLicenseStatus();
    
    // Load customization FIRST (for logo, social links, etc.)
    loadCustomizationFromBackend().then(() => {
      // THEN load theme (this will override customization colors if needed)
      loadThemeFromBackend();
    });
    
    // Check if trial expired
    const expired = isTrialExpired();
    if (expired) {
      setTrialExpired(true);
      setShowLicenseModal(true);
    }
  }, []);
  
  // Apply customization colors dynamically - ONLY if no custom theme is active
  useEffect(() => {
    if (customization) {
      // Check if custom theme is active (not default Matrix Green)
      const savedTheme = localStorage.getItem('current_theme');
      let hasCustomTheme = false;
      
      if (savedTheme) {
        try {
          const themeData = JSON.parse(savedTheme);
          // If theme is not default Matrix Green, don't override with customization
          hasCustomTheme = themeData.name && !themeData.name.includes('Matrix Green');
        } catch (e) {
          console.error('Failed to parse saved theme:', e);
        }
      }
      
      // Only apply customization colors if NO custom theme is active
      if (!hasCustomTheme) {
        console.log('ℹ️ Applying customization colors (no custom theme active)');
        document.documentElement.style.setProperty('--matrix-color', customization.matrixColor);
        document.documentElement.style.setProperty('--text-color', customization.textColor);
      } else {
        console.log('ℹ️ Skipping customization colors (custom theme is active)');
      }
    }
  }, [customization]);

  // PWA Install Prompt Handler - FIXED WITH BETTER ERROR HANDLING
  useEffect(() => {
    const handleBeforeInstallPrompt = (e) => {
      // Prevent default mini-infobar
      e.preventDefault();
      console.log('✅ PWA: beforeinstallprompt event fired');
      
      // Validate that prompt method exists
      if (e && typeof e.prompt === 'function') {
        // Stash the event in state
        setDeferredPrompt(e);
        // Show install button
        setShowPWAButton(true);
      } else {
        console.warn('⚠️ PWA: beforeinstallprompt event received but prompt() not available');
      }
    };

    const handleAppInstalled = () => {
      console.log('✅ PWA: App installed successfully!');
      // Hide button after installation
      setShowPWAButton(false);
      setDeferredPrompt(null);
    };

    // Check if we're in a PWA-compatible environment
    if ('serviceWorker' in navigator) {
      window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.addEventListener('appinstalled', handleAppInstalled);
    } else {
      console.log('ℹ️ PWA: Service Worker not supported in this browser');
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  // Handle PWA Install Button Click - IMPROVED USER EXPERIENCE
  const handlePWAInstallClick = async () => {
    console.log('🔘 PWA: Install button clicked');
    
    if (!deferredPrompt) {
      console.log('ℹ️ PWA: No install prompt available yet');
      alert('📱 Installation Tip:\n\n' +
            'To install this app:\n' +
            '• On Chrome/Edge Desktop: Look for install icon in address bar\n' +
            '• On Mobile: Tap browser menu → "Add to Home Screen"\n' +
            '• Installation makes the app run faster and work offline!');
      return;
    }

    console.log('📲 PWA: Showing install prompt...');
    
    try {
      // Ensure prompt() exists before calling
      if (typeof deferredPrompt.prompt !== 'function') {
        console.error('❌ PWA: prompt() method not available');
        alert('⚠️ PWA installation is not fully supported in this browser.\n\n' +
              'Try using Chrome or Edge for best experience.');
        return;
      }

      // Show the install prompt
      await deferredPrompt.prompt();
      
      // Wait for the user's response
      const { outcome } = await deferredPrompt.userChoice;
      console.log(`✅ PWA: User ${outcome === 'accepted' ? 'accepted' : 'dismissed'} install`);
      
      if (outcome === 'accepted') {
        alert('🎉 App installed successfully!\n\nYou can now find it on your home screen or app list.');
      }
      
      // Clear the deferred prompt
      setDeferredPrompt(null);
      setShowPWAButton(false);
      
    } catch (error) {
      console.error('❌ PWA: Error showing prompt:', error);
      alert('⚠️ Installation error occurred.\n\n' +
            'Try these alternatives:\n' +
            '• Browser menu → "Install app"\n' +
            '• Add to home screen from browser menu');
    }
  };

  // Fetch About content from API with SSE + POLLING FALLBACK
  useEffect(() => {
    console.log('🚀 GamingDemo: Initializing About content...');
    fetchAboutContent();
    
    // POLLING FALLBACK: Refresh every 10 seconds (TX Admin style)
    const pollingInterval = setInterval(() => {
      console.log('🔄 Polling: Refreshing About content...');
      fetchAboutContent();
    }, 10000);
    
    // Fetch About tags and Recent Streams
    fetchAboutTags();
    fetchRecentStreams();
    
    // Generate unique client ID for SSE connection
    const clientId = `gaming-demo-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    // SSE listener for real-time updates (INSTANT when it works)
    const sseUrl = `${process.env.REACT_APP_BACKEND_URL}/api/sse/${clientId}`;
    console.log('🔌 SSE: Connecting to:', sseUrl);
    
    const eventSource = new EventSource(sseUrl);
    
    eventSource.onopen = () => {
      console.log('✅ SSE: Connection opened!');
    };
    
    eventSource.addEventListener('about_content_update', (event) => {
      console.log('📝 SSE EVENT: about_content_update received!');
      console.log('📝 Event data:', event.data);
      
      try {
        const data = JSON.parse(event.data);
        console.log('📝 Parsed:', data);
        
        if (data.content) {
          const contentText = Array.isArray(data.content) 
            ? data.content.join(' • ')
            : data.content;
          console.log('✅ SSE UPDATE: Setting new content instantly!');
          setAboutContent(contentText);
        }
      } catch (error) {
        console.error('❌ SSE parse error:', error);
      }
    });
    
    // Schedule update listener
    eventSource.addEventListener('schedule_update', (event) => {
      console.log('📅 SSE EVENT: schedule_update received!');
      try {
        const data = JSON.parse(event.data);
        if (data.schedule) {
          setSchedule(data.schedule);
          console.log('✅ SSE UPDATE: Schedule updated instantly!', data.schedule);
        }
      } catch (error) {
        console.error('❌ SSE schedule parse error:', error);
      }
    });
    
    // Live status update listener
    eventSource.addEventListener('live_status_update', (event) => {
      console.log('🔴 SSE EVENT: live_status_update received!');
      try {
        const data = JSON.parse(event.data);
        setIsLive(data.is_live || false);
        setViewerCount(data.current_viewers || 0);
        console.log('✅ SSE UPDATE: Live status updated!', data);
      } catch (error) {
        console.error('❌ SSE live status parse error:', error);
      }
    });
    
    // Featured video update listener
    eventSource.addEventListener('featured_video_update', (event) => {
      console.log('🎬 SSE EVENT: featured_video_update received!');
      try {
        const data = JSON.parse(event.data);
        if (data.featured_video) {
          setFeaturedVideo(data.featured_video);
          console.log('✅ SSE UPDATE: Featured video updated!', data.featured_video);
        }
      } catch (error) {
        console.error('❌ SSE featured video parse error:', error);
      }
    });
    
    // Tags update listener
    eventSource.addEventListener('tags_update', (event) => {
      console.log('🏷️ SSE EVENT: tags_update received!');
      try {
        const data = JSON.parse(event.data);
        if (data.tags) {
          setAboutTags(data.tags);
          console.log('✅ SSE UPDATE: Tags updated!', data.tags);
        }
      } catch (error) {
        console.error('❌ SSE tags parse error:', error);
      }
    });
    
    // Streams update listener
    eventSource.addEventListener('streams_update', (event) => {
      console.log('🎮 SSE EVENT: streams_update received!');
      try {
        const data = JSON.parse(event.data);
        if (data.streams) {
          setRecentStreams(data.streams);
          console.log('✅ SSE UPDATE: Streams updated!', data.streams);
        }
      } catch (error) {
        console.error('❌ SSE streams parse error:', error);
      }
    });
    
    // Theme change listener - DYNAMICALLY apply without reload!
    eventSource.addEventListener('theme_changed', (event) => {
      console.log('🎨 SSE EVENT: theme_changed received!');
      try {
        const data = JSON.parse(event.data);
        console.log('✅ SSE UPDATE: Applying new theme instantly!', data);
        
        // Apply theme immediately without page reload
        if (data.theme) {
          applyTheme(data.theme);
          
          // Show success notification
          const notification = document.createElement('div');
          notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 255, 0, 0.9);
            color: #000;
            padding: 15px 25px;
            border-radius: 8px;
            font-weight: bold;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
          `;
          notification.textContent = '🎨 Theme Updated!';
          document.body.appendChild(notification);
          
          setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
          }, 2000);
        }
      } catch (error) {
        console.error('❌ SSE theme parse error:', error);
      }
    });
    
    eventSource.onerror = (error) => {
      console.error('❌ SSE error - Polling fallback active');
    };
    
    return () => {
      console.log('🔌 Cleanup: Closing connections');
      clearInterval(pollingInterval);
      eventSource.close();
    };
  }, []);
  
  const fetchAboutContent = async () => {
    console.log('📥 Fetching About content from API...');
    try {
      // Add cache buster to force fresh data
      const timestamp = Date.now();
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/content/about?t=${timestamp}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      console.log('📥 About content received:', data);
      
      if (data.content && data.content.length > 0) {
        // Convert array to string with bullet separator
        const contentText = Array.isArray(data.content) 
          ? data.content.join(' • ')
          : data.content;
        console.log('📥 Setting About content:', contentText);
        setAboutContent(contentText);
      } else {
        console.warn('⚠️ No content in response, using fallback');
        setAboutContent("Serbia-based competitive FORTNITE player specializing in Rocket Racing tournaments.");
      }
    } catch (error) {
      console.error('Failed to fetch about content:', error);
      setAboutContent("Serbia-based competitive FORTNITE player specializing in Rocket Racing tournaments.");
    }
  };
  
  const fetchAboutTags = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/content/tags`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      if (data.tags && data.tags.length > 0) {
        setAboutTags(data.tags);
        console.log('✅ Tags loaded from backend:', data.tags);
      }
    } catch (error) {
      console.error('Failed to fetch about tags:', error);
    }
  };
  
  const fetchRecentStreams = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/streams/recent`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      if (data.streams && data.streams.length > 0) {
        setRecentStreams(data.streams);
        console.log('✅ Recent streams loaded from backend:', data.streams.length);
      }
    } catch (error) {
      console.error('Failed to fetch recent streams:', error);
    }
  };

  // Featured Video - REMOVED

  // Simulate live viewer count updates
  useEffect(() => {
    const interval = setInterval(() => {
      setViewerCount(prev => prev + Math.floor(Math.random() * 20 - 10));
      setFollowerCount(prev => prev + Math.floor(Math.random() * 5));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Recent Streams - Load from backend dynamically
  const [recentStreams, setRecentStreams] = useState([]);

  // Schedule state (fetched from backend)
  const [schedule, setSchedule] = useState([
    { day: 'MON', time: '19:00', game: 'FORTNITE' },
    { day: 'TUE', time: '20:00', game: 'FORTNITE ROCKET RACING' },
    { day: 'WED', time: '19:30', game: 'FORTNITE CREATIVE' },
    { day: 'THU', time: '20:00', game: 'FORTNITE BATTLE ROYALE' },
    { day: 'FRI', time: '19:00', game: 'FORTNITE Weekend' },
    { day: 'SAT', time: '18:00', game: 'FORTNITE ROCKET RACING Tournament' },
    { day: 'SUN', time: 'REST', game: 'No Stream' }
  ]);
  
  // Fetch schedule from backend on mount - PUBLIC endpoint
  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/schedule`);
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.schedule && data.schedule.length > 0) {
            setSchedule(data.schedule);
            console.log('✅ Schedule loaded from backend:', data.schedule);
          }
        }
      } catch (error) {
        console.error('Failed to fetch schedule:', error);
        // Keep default schedule on error
      }
    };
    fetchSchedule();
  }, []);

  // Fetch YouTube videos from backend
  useEffect(() => {
    const fetchYouTubeVideos = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/youtube/latest-videos`);
        if (response.ok) {
          const videos = await response.json();
          if (videos && videos.length > 0) {
            // Map YouTube API response to recentStreams format
            const mappedStreams = videos.slice(0, 6).map(video => ({
              id: video.video_id,
              title: video.title,
              game: 'FORTNITE', // Default game
              thumbnail: video.thumbnail_url,
              duration: formatDuration(video.duration),
              views: video.view_count || '0',
              videoUrl: video.watch_url
            }));
            setRecentStreams(mappedStreams);
            console.log('✅ YouTube videos loaded:', mappedStreams.length);
          }
        }
      } catch (error) {
        console.error('Failed to fetch YouTube videos:', error);
      }
    };
    fetchYouTubeVideos();
  }, []);

  // Helper function to format ISO 8601 duration to readable format
  const formatDuration = (isoDuration) => {
    if (!isoDuration) return '0:00';
    const match = isoDuration.match(/PT(\d+H)?(\d+M)?(\d+S)?/);
    if (!match) return '0:00';
    
    const hours = (match[1] || '').replace('H', '');
    const minutes = (match[2] || '0M').replace('M', '');
    const seconds = (match[3] || '0S').replace('S', '');
    
    if (hours) {
      return `${hours}:${minutes.padStart(2, '0')}:${seconds.padStart(2, '0')}`;
    }
    return `${minutes}:${seconds.padStart(2, '0')}`;
  };

  return (
    <div className="gaming-demo">
      {/* Neon Fade Line at Top */}
      <div className="neon-fade-line"></div>
      
      {/* Language Switcher - Floating Left */}
      <LanguageSwitcher />
      
      {/* License Activation Badge - Top Right */}
      <LicenseActivation />
      
      {/* Trial Status removed from top - moved to bottom */}
      
      {/* Matrix Rain Background - ENABLED */}
      <div className="matrix-background-demo">
        <MatrixRain />
      </div>
      
      <motion.header 
        className="demo-header gaming-header"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        {/* Live Status - ABOVE channel name */}
        <div className="live-status-top">
          {isLive && (
            <div className="live-indicator gaming-live">
              <span className="live-dot"></span>
              {t('liveNow')} - {viewerCount.toLocaleString()} {t('viewers')}
            </div>
          )}
        </div>
        
        <div className="header-brand">
          <h1>
            {customization.userName}
            <Logo3D logoUrl={customization.logoUrl} userName={customization.userName} licenseType={licenseType} />
          </h1>
        </div>
        
        {/* Header Buttons - Hidden in Distribution Mode */}
        {!customization.distributionMode && (
          <motion.button
            className="admin-access-btn"
            onClick={() => setShowAdminPanel(true)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title={t('admin')}
          >
            ⚙️ {t('admin')}
          </motion.button>
        )}
      </motion.header>

      {/* Main Content Container */}
      <div className="container">
        {/* Notification Subscription System */}
        <NotificationSubscription />

        {/* Viewer Menu System with Point-based Rewards & WA Chat */}
        <motion.section 
          className="viewer-menu-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <ViewerMenu />
        </motion.section>

        {/* About Section - COMPACT VERSION with DYNAMIC Content */}
        {customization.aboutSectionTitle && (
        <motion.section 
          className="about-remza-compact"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          <div className="about-compact-container">
            <motion.h2 
              className="about-compact-title"
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5 }}
            >
              🎮 {t('aboutTitle')}
            </motion.h2>
            
            <div className="about-compact-content">
              <p className="about-bio">
                {aboutContent}
              </p>
              
              <div className="about-tags">
                {aboutTags.map((tag, index) => (
                  <span key={`${tag.icon}-${tag.text}-${index}`} className="tag">
                    {tag.icon} {tag.text}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </motion.section>
        )}

        {/* Featured Video Section - REMOVED */}

        {/* Recent Streams */}
        <motion.section 
          className="recent-streams"
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <h2>🎮 {t('recentStreams')}</h2>
          <div className="streams-grid">
            {recentStreams.map((stream, index) => (
              <motion.div 
                key={`${stream.id}-${index}`}
                className="stream-card matrix-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.6 + 0.1 * index }}
                whileHover={{ scale: 1.05 }}
              >
                <div className="stream-thumbnail">
                  <img src={stream.thumbnail} alt={stream.title} />
                  <div className="stream-duration">{stream.duration}</div>
                  <div className="stream-views">{stream.views} {t('views')}</div>
                </div>
                <div className="stream-details">
                  <h4>{stream.title}</h4>
                  <p className="stream-game">🎯 {stream.game}</p>
                  <button 
                    className="matrix-button watch-btn"
                    onClick={() => {
                      try {
                        console.log(`Opening stream: ${stream.title} - ${stream.videoUrl}`);
                        if (stream.videoUrl && stream.videoUrl.includes('youtube.com')) {
                          window.open(stream.videoUrl, '_blank', 'noopener,noreferrer');
                        } else {
                          console.error('Invalid YouTube URL:', stream.videoUrl);
                        }
                      } catch (error) {
                        console.error('Error opening stream:', error);
                      }
                    }}
                  >
                    {t('watchHighlights')}
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Community Section */}
        <motion.section 
          className="community-section"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
        >
          <h2>🎯 {t('joinTheCommunity')}</h2>
          <div className="community-links">
            {customization.communityLinks?.discord && (
              <motion.button 
                className="matrix-button community-btn discord"
                whileHover={{ scale: 1.05 }}
                onClick={() => window.open(customization.communityLinks.discord, '_blank')}
              >
                💬 {t('discordServer')}
              </motion.button>
            )}
            {customization.communityLinks?.youtube && (
              <motion.button 
                className="matrix-button community-btn youtube"
                whileHover={{ scale: 1.05 }}
                onClick={() => window.open(customization.communityLinks.youtube, '_blank')}
              >
                📺 {t('youtubeChannel')}
              </motion.button>
            )}
            {customization.communityLinks?.youtube && (
              <motion.button 
                className="matrix-button community-btn youtube-follow"
                whileHover={{ scale: 1.05 }}
                onClick={() => window.open(`${customization.communityLinks.youtube}?sub_confirmation=1`, '_blank')}
              >
                🔔 {t('followChannel')}
              </motion.button>
            )}
            {customization.communityLinks?.twitch && (
              <motion.button 
                className="matrix-button community-btn twitch"
                whileHover={{ scale: 1.05 }}
                onClick={() => window.open(customization.communityLinks.twitch, '_blank')}
              >
                🟣 {t('twitchChannel')}
              </motion.button>
            )}
            {customization.communityLinks?.twitter && (
              <motion.button 
                className="matrix-button community-btn twitter"
                whileHover={{ scale: 1.05 }}
                onClick={() => window.open(customization.communityLinks.twitter, '_blank')}
              >
                🐦 {t('twitterX')}
              </motion.button>
            )}
          </div>
        </motion.section>

        {/* Support the Streamer Section - Bottom of Page */}
        <motion.section 
          className="support-streamer-section bottom-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.0 }}
        >
          <div className="support-container">
            <div className="support-content">
              <h2 className="support-title">💚 {t('supportStreamer')}</h2>
              <p className="support-description">
                {t('supportDesc')}
              </p>
              <motion.button
                className="support-streamer-btn"
                onClick={() => setShowDonationModal(true)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                💰 {t('donateNow')}
              </motion.button>
            </div>
          </div>
        </motion.section>

        {/* Stream Schedule Widget */}
        <ScheduleWidget />

        {/* Points Tracker - User Engagement */}
        {currentUser && (
          <PointsTracker 
            user={currentUser}
            points={currentUser.points || 0}
            level={currentUser.level || 1}
            onPointsUpdate={handlePointsUpdate}
          />
        )}

        {/* Leaderboard Section */}
        <Leaderboard />

        {/* Polls & Predictions Widgets */}
        <PollsWidget user={currentUser} />
        <PredictionsWidget user={currentUser} />

        {/* Social Links */}
        <SocialLinks />

        {/* Trial Status - Bottom of Page */}
        <div className="bottom-status-container">
          <TrialStatus 
            onExpired={() => {
              setTrialExpired(true);
              setShowLicenseModal(true);
            }}
          />
        </div>

        {/* PWA Install Button - ONLY if Admin enables it */}
        {customization.enablePWAInstall && (
          <motion.section 
            className="pwa-install-section"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="pwa-install-container">
              <h3 className="pwa-install-title">{customization.pwaInstallTitle || '📱 Install App'}</h3>
              <p className="pwa-install-description">
                Get the full experience! Install our Progressive Web App for instant access, offline support, and a native app feel.
              </p>
              <motion.button
                className="pwa-install-button-bottom"
                onClick={handlePWAInstallClick}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                📲 Install App
              </motion.button>
              <p className="pwa-install-note">
                {showPWAButton 
                  ? "✅ Installation available! Click to install." 
                  : "ℹ️ Installation will be available when browser supports it."}
              </p>
            </div>
          </motion.section>
        )}
      </div>
      
      {/* Admin Panel Modal Overlay */}
      <AnimatePresence>
        {showAdminPanel && (
          <motion.div
            className="admin-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowAdminPanel(false)}
          >
            <motion.div
              className="admin-modal-content"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="admin-modal-header">
                <h2>{customization.adminPanelTitle || '🎮 Admin Panel'}</h2>
                <button
                  className="admin-close-btn"
                  onClick={() => setShowAdminPanel(false)}
                >
                  ✕
                </button>
              </div>
              
              <div className="admin-modal-body">
                <AdminPanelWrapper />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Donation Modal */}
      <DonationModal 
        isOpen={showDonationModal} 
        onClose={() => setShowDonationModal(false)} 
      />

      {/* Social Links Footer */}
      <SocialLinksFooter links={customization.communityLinks} />

      {/* Footer */}
      <footer className="demo-footer">
        <p>
          {customization.copyrightText || '© 2025. All rights reserved.'}
        </p>
        <div className="powered-by-019">
          <span className="powered-text">MADE BY</span>
          <span className="company-name-019">019SoluTionS</span>
        </div>
      </footer>

      {/* Version Checker */}
      <VersionChecker />
      
      {/* License Activation Modal */}
      <LicenseModal 
        isOpen={showLicenseModal}
        onClose={() => !trialExpired && setShowLicenseModal(false)}
        onActivated={() => {
          setTrialExpired(false);
          setShowLicenseModal(false);
          window.location.reload(); // Refresh to apply changes
        }}
      />
      
      {/* Customization Modal */}
      <CustomizationModal 
        isOpen={showCustomizationModal}
        onClose={() => setShowCustomizationModal(false)}
        onSave={(newCustomization) => {
          setCustomization(newCustomization);
          window.location.reload(); // Reload to apply changes
        }}
      />
    </div>
  );
};

export default GamingDemo;