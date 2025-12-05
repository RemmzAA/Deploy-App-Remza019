// License Manager - Trial & Full Version System
// 019 Solutions - Customizable Streamer Website

const TRIAL_DURATION_DAYS = 7;
const LICENSE_STORAGE_KEY = 'remza019_license';

/**
 * Generate a unique trial license key
 */
export const generateTrialKey = () => {
  const randomPart = Math.random().toString(36).substring(2, 7).toUpperCase();
  const timestampPart = Date.now().toString(36).toUpperCase();
  return `TRIAL-${randomPart}-${timestampPart}`;
};

/**
 * Initialize license on first PWA install
 */
export const initializeLicense = () => {
  const existingLicense = getLicenseData();
  
  if (!existingLicense) {
    const trialKey = generateTrialKey();
    const trialStartDate = new Date().toISOString();
    
    const licenseData = {
      licenseKey: trialKey,
      licenseType: 'TRIAL',
      trialStartDate: trialStartDate,
      trialExpired: false,
      customization: {
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
      }
    };
    
    localStorage.setItem(LICENSE_STORAGE_KEY, JSON.stringify(licenseData));
    console.log('✅ Trial license initialized:', trialKey);
    return licenseData;
  }
  
  return existingLicense;
};

/**
 * Sanitize and validate string input
 */
const sanitizeString = (str, maxLength = 500) => {
  if (typeof str !== 'string') return '';
  // Remove any HTML tags and script tags
  const cleaned = str.replace(/<[^>]*>/g, '').trim();
  return cleaned.substring(0, maxLength);
};

/**
 * Validate license data structure
 */
const validateLicenseData = (data) => {
  if (!data || typeof data !== 'object') return false;
  
  // Check required fields
  if (!data.licenseKey || typeof data.licenseKey !== 'string') return false;
  if (!data.licenseType || !['TRIAL', 'FULL'].includes(data.licenseType)) return false;
  
  // Validate customization object
  if (data.customization && typeof data.customization !== 'object') return false;
  
  return true;
};

/**
 * Get license data from localStorage - SECURE VERSION
 */
export const getLicenseData = () => {
  try {
    const data = localStorage.getItem(LICENSE_STORAGE_KEY);
    if (!data) return null;
    
    const parsed = JSON.parse(data);
    
    // Validate structure
    if (!validateLicenseData(parsed)) {
      console.warn('⚠️ Invalid license data structure detected');
      localStorage.removeItem(LICENSE_STORAGE_KEY);
      return null;
    }
    
    return parsed;
  } catch (error) {
    console.error('❌ Error reading license data:', error);
    localStorage.removeItem(LICENSE_STORAGE_KEY);
    return null;
  }
};

/**
 * Check if trial has expired
 */
export const isTrialExpired = () => {
  const licenseData = getLicenseData();
  
  if (!licenseData) {
    return false; // No license yet
  }
  
  if (licenseData.licenseType === 'FULL') {
    return false; // Full license never expires
  }
  
  const startDate = new Date(licenseData.trialStartDate);
  const currentDate = new Date();
  const daysPassed = Math.floor((currentDate - startDate) / (1000 * 60 * 60 * 24));
  
  return daysPassed >= TRIAL_DURATION_DAYS;
};

/**
 * Get remaining trial days
 */
export const getRemainingTrialDays = () => {
  const licenseData = getLicenseData();
  
  if (!licenseData || licenseData.licenseType === 'FULL') {
    return null;
  }
  
  const startDate = new Date(licenseData.trialStartDate);
  const currentDate = new Date();
  const daysPassed = Math.floor((currentDate - startDate) / (1000 * 60 * 60 * 24));
  const remainingDays = TRIAL_DURATION_DAYS - daysPassed;
  
  return remainingDays > 0 ? remainingDays : 0;
};

/**
 * Validate and activate full license key - WITH BACKEND VERIFICATION
 */
export const activateFullLicense = async (licenseKey) => {
  // License key format: FULL-XXXXX-XXXXX-XXXXX
  const licensePattern = /^FULL-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$/;
  
  if (!licensePattern.test(licenseKey)) {
    return {
      success: false,
      message: '❌ Invalid license key format. Format: FULL-XXXXX-XXXXX-XXXXX'
    };
  }
  
  try {
    // Verify with backend
    const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
    const response = await fetch(`${backendUrl}/api/license/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ license_key: licenseKey })
    });
    
    const result = await response.json();
    
    if (!result.success || !result.valid) {
      return {
        success: false,
        message: result.message || '❌ License key verification failed'
      };
    }
    
    // License is valid - activate locally
    const licenseData = getLicenseData() || {};
    
    licenseData.licenseKey = licenseKey;
    licenseData.licenseType = 'FULL';
    licenseData.trialExpired = false;
    licenseData.activationDate = new Date().toISOString();
    licenseData.backendVerified = true;
    licenseData.verifiedAt = new Date().toISOString();
    
    localStorage.setItem(LICENSE_STORAGE_KEY, JSON.stringify(licenseData));
    
    console.log('✅ Full license activated and verified:', licenseKey);
    
    return {
      success: true,
      message: '🎉 License activated successfully! Thank you for purchasing!'
    };
    
  } catch (error) {
    console.error('❌ License verification error:', error);
    return {
      success: false,
      message: '❌ Unable to verify license. Please check your internet connection.'
    };
  }
};

/**
 * Validate hex color format
 */
const isValidHexColor = (color) => {
  return /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(color);
};

/**
 * Validate URL format (basic check)
 */
const isValidUrl = (url) => {
  if (!url) return true; // Empty is OK
  try {
    // Check if it's a data URL (for base64 images)
    if (url.startsWith('data:image/')) return true;
    // Check if it's a relative path
    if (url.startsWith('/')) return true;
    // Check if it's a valid URL
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Update customization settings - SECURE VERSION
 */
export const updateCustomization = (customizationData) => {
  const licenseData = getLicenseData();
  
  if (!licenseData) {
    return {
      success: false,
      message: '❌ No license found. Please initialize first.'
    };
  }
  
  // Sanitize and validate all inputs
  const sanitizedData = {
    userName: customizationData.userName ? sanitizeString(customizationData.userName, 50) : licenseData.customization.userName,
    matrixColor: isValidHexColor(customizationData.matrixColor) ? customizationData.matrixColor : '#00ff00',
    textColor: isValidHexColor(customizationData.textColor) ? customizationData.textColor : '#00ff00',
    logoUrl: isValidUrl(customizationData.logoUrl) ? customizationData.logoUrl : licenseData.customization.logoUrl,
    youtubeChannelId: customizationData.youtubeChannelId ? sanitizeString(customizationData.youtubeChannelId, 100) : '',
    discordLink: customizationData.discordLink ? sanitizeString(customizationData.discordLink, 200) : '',
    socialLinks: {
      twitter: customizationData.socialLinks?.twitter ? sanitizeString(customizationData.socialLinks.twitter, 100) : '',
      instagram: customizationData.socialLinks?.instagram ? sanitizeString(customizationData.socialLinks.instagram, 100) : '',
      twitch: customizationData.socialLinks?.twitch ? sanitizeString(customizationData.socialLinks.twitch, 100) : '',
      tiktok: customizationData.socialLinks?.tiktok ? sanitizeString(customizationData.socialLinks.tiktok, 100) : ''
    }
  };
  
  licenseData.customization = sanitizedData;
  
  try {
    localStorage.setItem(LICENSE_STORAGE_KEY, JSON.stringify(licenseData));
    console.log('✅ Customization updated (sanitized)');
    
    return {
      success: true,
      message: '✅ Settings saved successfully!'
    };
  } catch (error) {
    console.error('❌ Error saving customization:', error);
    return {
      success: false,
      message: '❌ Failed to save settings. Please try again.'
    };
  }
};

/**
 * Get customization settings
 */
export const getCustomization = () => {
  const licenseData = getLicenseData();
  
  if (!licenseData || !licenseData.customization) {
    return {
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
  }
  
  return licenseData.customization;
};

/**
 * Reset trial (for testing purposes only)
 */
export const resetTrial = () => {
  localStorage.removeItem(LICENSE_STORAGE_KEY);
  console.log('🔄 Trial reset - removed license data');
  return initializeLicense();
};

/**
 * Get license status summary
 */
export const getLicenseStatus = () => {
  const licenseData = getLicenseData();
  
  if (!licenseData) {
    return {
      isActive: false,
      type: 'NONE',
      message: 'No license found'
    };
  }
  
  if (licenseData.licenseType === 'FULL') {
    return {
      isActive: true,
      type: 'FULL',
      message: '✅ Full License Active',
      licenseKey: licenseData.licenseKey
    };
  }
  
  const expired = isTrialExpired();
  const remainingDays = getRemainingTrialDays();
  
  if (expired) {
    return {
      isActive: false,
      type: 'TRIAL_EXPIRED',
      message: '❌ Trial Expired - Purchase Full License',
      licenseKey: licenseData.licenseKey
    };
  }
  
  return {
    isActive: true,
    type: 'TRIAL',
    message: `⏳ Trial Active - ${remainingDays} days remaining`,
    remainingDays: remainingDays,
    licenseKey: licenseData.licenseKey
  };
};

export default {
  generateTrialKey,
  initializeLicense,
  getLicenseData,
  isTrialExpired,
  getRemainingTrialDays,
  activateFullLicense,
  updateCustomization,
  getCustomization,
  resetTrial,
  getLicenseStatus
};
