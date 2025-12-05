import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getCustomization, updateCustomization } from '../utils/licenseManager';
import './AdminCustomizationPanel.css';

const AdminCustomizationPanel = () => {
  const [formData, setFormData] = useState({
    userName: '',
    matrixColor: '#00ff00',
    textColor: '#00ff00',
    logoUrl: '',
    youtubeChannelId: '',
    discordLink: '',
    socialLinks: {
      twitter: '',
      instagram: '',
      twitch: '',
      tiktok: ''
    }
  });

  const [logoPreview, setLogoPreview] = useState('');
  const [message, setMessage] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);

  useEffect(() => {
    const customization = getCustomization();
    setFormData(customization);
    setLogoPreview(customization.logoUrl);
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    if (name.startsWith('social_')) {
      const socialKey = name.replace('social_', '');
      setFormData(prev => ({
        ...prev,
        socialLinks: {
          ...prev.socialLinks,
          [socialKey]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleLogoChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const MAX_FILE_SIZE = 2 * 1024 * 1024;
    const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
    
    if (!ALLOWED_TYPES.includes(file.type)) {
      setMessage('❌ Invalid file type. Please upload PNG, JPG, or WebP.');
      setIsSuccess(false);
      return;
    }
    
    if (file.size > MAX_FILE_SIZE) {
      setMessage('❌ File too large. Maximum size is 2MB.');
      setIsSuccess(false);
      return;
    }
    
    setMessage('');
    
    const reader = new FileReader();
    reader.onloadend = () => {
      setLogoPreview(reader.result);
    };
    reader.onerror = () => {
      setMessage('❌ Error reading file.');
      setIsSuccess(false);
    };
    reader.readAsDataURL(file);
  };

  const handleSave = async () => {
    const finalData = {
      ...formData,
      logoUrl: logoPreview || formData.logoUrl
    };

    try {
      // Save to backend
      const token = localStorage.getItem('admin_token');
      
      if (!token) {
        setMessage('❌ Not authenticated! Please login to Admin panel first.');
        setIsSuccess(false);
        return;
      }
      
      console.log('💾 Saving customization to backend...', finalData);
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/customization/save`, {
        method: 'POST',
        mode: 'cors',
        credentials: 'include',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(finalData)
      });

      console.log('📡 Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Backend error:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      console.log('✅ Backend response:', result);
      
      if (result.success) {
        // Also save to localStorage as backup
        updateCustomization(finalData);
        
        setMessage('✅ Customization saved successfully! Reloading page...');
        setIsSuccess(true);

        setTimeout(() => {
          window.location.reload();
        }, 1500);
      } else {
        const errorMsg = result.message || result.detail || 'Unknown error';
        setMessage('❌ Failed to save: ' + errorMsg);
        setIsSuccess(false);
      }
    } catch (error) {
      console.error('❌ Save customization error:', error);
      
      // Fallback to localStorage only
      const result = updateCustomization(finalData);
      setMessage('⚠️ ' + result.message + ' (Offline mode - backend unavailable)');
      setIsSuccess(result.success);
      
      if (result.success) {
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      }
    }
  };

  const handleReset = () => {
    if (window.confirm('Reset to default settings?')) {
      const defaultSettings = {
        userName: '019 Solutions',
        matrixColor: '#00ff00',
        textColor: '#00ff00',
        logoUrl: '/remza-logo.png',
        youtubeChannelId: '',
        discordLink: '',
        socialLinks: {
          twitter: '',
          instagram: '',
          twitch: '',
          tiktok: ''
        }
      };
      
      setFormData(defaultSettings);
      setLogoPreview('/remza-logo.png');
      setMessage('✅ Reset to defaults');
      setIsSuccess(true);
    }
  };

  return (
    <div className="admin-customization-panel">
      <div className="customization-header">
        <h2>🎨 Site Customization</h2>
        <p>Customize your gaming site appearance and branding</p>
      </div>

      <div className="customization-grid">
        
        {/* Site Name */}
        <div className="custom-card">
          <h3>📝 Site Name</h3>
          <input
            type="text"
            name="userName"
            value={formData.userName}
            onChange={handleInputChange}
            placeholder="Your Gaming Name"
            maxLength={50}
          />
          <span className="hint">Appears in header and title</span>
        </div>

        {/* Matrix Color */}
        <div className="custom-card">
          <h3>🌈 Matrix Effect Color</h3>
          <div className="color-input-group">
            <input
              type="color"
              name="matrixColor"
              value={formData.matrixColor}
              onChange={handleInputChange}
            />
            <input
              type="text"
              value={formData.matrixColor}
              onChange={handleInputChange}
              name="matrixColor"
              placeholder="#00ff00"
            />
          </div>
          <span className="hint">Falling rain effect color</span>
        </div>

        {/* Text Color */}
        <div className="custom-card">
          <h3>🎨 Text Color</h3>
          <div className="color-input-group">
            <input
              type="color"
              name="textColor"
              value={formData.textColor}
              onChange={handleInputChange}
            />
            <input
              type="text"
              value={formData.textColor}
              onChange={handleInputChange}
              name="textColor"
              placeholder="#00ff00"
            />
          </div>
          <span className="hint">Main text and headings color</span>
        </div>

        {/* Logo Upload */}
        <div className="custom-card logo-card">
          <h3>🖼️ Logo</h3>
          {logoPreview && (
            <div className="logo-preview-admin">
              <img src={logoPreview} alt="Logo" />
            </div>
          )}
          <input
            type="file"
            id="admin-logo-upload"
            accept="image/*"
            onChange={handleLogoChange}
            style={{display: 'none'}}
          />
          <label htmlFor="admin-logo-upload" className="upload-btn">
            📤 Upload Logo
          </label>
          <span className="hint">Square, 512x512px, PNG recommended</span>
        </div>

        {/* YouTube */}
        <div className="custom-card">
          <h3>📺 YouTube Channel</h3>
          <input
            type="text"
            name="youtubeChannelId"
            value={formData.youtubeChannelId}
            onChange={handleInputChange}
            placeholder="UCxxxxx"
          />
          <span className="hint">Your YouTube Channel ID</span>
        </div>

        {/* Discord */}
        <div className="custom-card">
          <h3>💬 Discord Server</h3>
          <input
            type="text"
            name="discordLink"
            value={formData.discordLink}
            onChange={handleInputChange}
            placeholder="discord.gg/xxxxx"
          />
          <span className="hint">Discord invite link</span>
        </div>

        {/* Social - Twitter */}
        <div className="custom-card">
          <h3>🐦 Twitter/X</h3>
          <input
            type="text"
            name="social_twitter"
            value={formData.socialLinks.twitter}
            onChange={handleInputChange}
            placeholder="@YourHandle"
          />
        </div>

        {/* Social - Instagram */}
        <div className="custom-card">
          <h3>📷 Instagram</h3>
          <input
            type="text"
            name="social_instagram"
            value={formData.socialLinks.instagram}
            onChange={handleInputChange}
            placeholder="@YourHandle"
          />
        </div>

        {/* Social - Twitch */}
        <div className="custom-card">
          <h3>🎮 Twitch</h3>
          <input
            type="text"
            name="social_twitch"
            value={formData.socialLinks.twitch}
            onChange={handleInputChange}
            placeholder="Username"
          />
        </div>

        {/* Social - TikTok */}
        <div className="custom-card">
          <h3>🎵 TikTok</h3>
          <input
            type="text"
            name="social_tiktok"
            value={formData.socialLinks.tiktok}
            onChange={handleInputChange}
            placeholder="@YourHandle"
          />
        </div>

      </div>

      {/* Message */}
      {message && (
        <motion.div
          className={`admin-custom-message ${isSuccess ? 'success' : 'error'}`}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {message}
        </motion.div>
      )}

      {/* Actions */}
      <div className="customization-actions">
        <button onClick={handleSave} className="btn-save">
          💾 Save Changes
        </button>
        <button onClick={handleReset} className="btn-reset">
          🔄 Reset to Default
        </button>
      </div>
    </div>
  );
};

export default AdminCustomizationPanel;
