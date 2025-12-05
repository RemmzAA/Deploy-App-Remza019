import React, { useState, useEffect } from 'react';
import './VersionChecker.css';

const VersionChecker = () => {
  const [versionInfo, setVersionInfo] = useState(null);
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [checking, setChecking] = useState(false);
  const [isElectron, setIsElectron] = useState(false);

  useEffect(() => {
    // Check if running in Electron
    if (window.electronAPI) {
      setIsElectron(true);
      initElectronVersion();
    } else {
      checkVersion();
    }
    
    // Check for updates every 30 minutes
    const interval = setInterval(() => {
      if (window.electronAPI) {
        initElectronVersion();
      } else {
        checkVersion();
      }
    }, 30 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  const initElectronVersion = async () => {
    try {
      const version = await window.electronAPI.getAppVersion();
      const installationId = await window.electronAPI.getInstallationId();
      
      setVersionInfo({
        version: version,
        version_name: 'Desktop Edition',
        installation_id: installationId,
        platform: window.electronAPI.platform || 'desktop'
      });
      
      // Listen for announcements from Electron
      if (window.electronAPI.onShowAnnouncement) {
        window.electronAPI.onShowAnnouncement((message) => {
          alert(`📢 Announcement: ${message}`);
        });
      }
    } catch (error) {
      console.error('Electron version init failed:', error);
    }
  };

  const checkVersion = async () => {
    try {
      setChecking(true);
      
      // Get current version
      const currentResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/version/current`);
      const current = await currentResponse.json();
      
      setVersionInfo(current);
      
      // Check if update is available
      const updateResponse = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/version/check-update?current_version=${current.version}`
      );
      const updateInfo = await updateResponse.json();
      
      setUpdateAvailable(updateInfo.is_update_available);
      
    } catch (error) {
      console.error('Version check failed:', error);
    } finally {
      setChecking(false);
    }
  };

  if (!versionInfo) {
    return null;
  }

  return (
    <div className="version-checker">
      <div className="version-info">
        {isElectron && <span className="desktop-badge">💻 Desktop</span>}
        <span className="version-label">v{versionInfo.version}</span>
        <span className="version-name">{versionInfo.version_name}</span>
      </div>
      
      {updateAvailable && (
        <div 
          className="update-badge" 
          onClick={() => {
            if (window.electronAPI) {
              window.electronAPI.checkForUpdates();
            } else {
              window.open('https://019solutions.com/downloads', '_blank');
            }
          }}
        >
          🔄 Update Available
        </div>
      )}
      
      {checking && (
        <div className="checking-badge">
          ⏳ Checking...
        </div>
      )}
    </div>
  );
};

export default VersionChecker;
