/**
 * REMZA019 Gaming - Cookie Management
 * Secure cookie storage for user sessions and preferences
 */

const COOKIE_OPTIONS = {
  secure: true, // HTTPS only
  sameSite: 'Lax',
  maxAge: 30 * 24 * 60 * 60 // 30 days
};

export const CookieManager = {
  /**
   * Set a cookie
   */
  set: (name, value, options = {}) => {
    const opts = { ...COOKIE_OPTIONS, ...options };
    let cookie = `${name}=${encodeURIComponent(JSON.stringify(value))}`;
    
    if (opts.maxAge) {
      cookie += `; max-age=${opts.maxAge}`;
    }
    
    if (opts.path) {
      cookie += `; path=${opts.path}`;
    } else {
      cookie += '; path=/';
    }
    
    if (opts.secure && window.location.protocol === 'https:') {
      cookie += '; secure';
    }
    
    if (opts.sameSite) {
      cookie += `; samesite=${opts.sameSite}`;
    }
    
    document.cookie = cookie;
    
    // Also store in localStorage as backup
    try {
      localStorage.setItem(name, JSON.stringify(value));
    } catch (e) {
      console.error('localStorage not available:', e);
    }
  },

  /**
   * Get a cookie value
   */
  get: (name) => {
    // Try cookie first
    const nameEQ = name + "=";
    const cookies = document.cookie.split(';');
    
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim();
      if (cookie.indexOf(nameEQ) === 0) {
        try {
          return JSON.parse(decodeURIComponent(cookie.substring(nameEQ.length)));
        } catch (e) {
          return cookie.substring(nameEQ.length);
        }
      }
    }
    
    // Fallback to localStorage
    try {
      const stored = localStorage.getItem(name);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (e) {
      console.error('Error reading from storage:', e);
    }
    
    return null;
  },

  /**
   * Remove a cookie
   */
  remove: (name) => {
    document.cookie = `${name}=; max-age=0; path=/`;
    
    // Also remove from localStorage
    try {
      localStorage.removeItem(name);
    } catch (e) {
      console.error('Error removing from storage:', e);
    }
  },

  /**
   * Check if cookie exists
   */
  exists: (name) => {
    return CookieManager.get(name) !== null;
  },

  /**
   * Clear all cookies (logout)
   */
  clearAll: () => {
    const cookies = document.cookie.split(';');
    
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i];
      const eqPos = cookie.indexOf('=');
      const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
      document.cookie = `${name}=; max-age=0; path=/`;
    }
    
    // Clear localStorage
    try {
      localStorage.clear();
    } catch (e) {
      console.error('Error clearing storage:', e);
    }
  }
};

// User-specific cookie helpers
export const UserCookies = {
  /**
   * Save user session
   */
  saveUser: (user) => {
    CookieManager.set('viewer_user', user, { maxAge: 30 * 24 * 60 * 60 }); // 30 days
  },

  /**
   * Get current user
   */
  getUser: () => {
    return CookieManager.get('viewer_user');
  },

  /**
   * Update user data
   */
  updateUser: (updates) => {
    const currentUser = UserCookies.getUser();
    if (currentUser) {
      const updatedUser = { ...currentUser, ...updates };
      UserCookies.saveUser(updatedUser);
      return updatedUser;
    }
    return null;
  },

  /**
   * Logout user
   */
  logout: () => {
    CookieManager.remove('viewer_user');
  },

  /**
   * Check if user is logged in
   */
  isLoggedIn: () => {
    const user = UserCookies.getUser();
    return user && user.user_id;
  }
};

// Preferences cookie helpers
export const PreferencesCookies = {
  /**
   * Save user preferences
   */
  savePreferences: (prefs) => {
    CookieManager.set('user_preferences', prefs, { maxAge: 365 * 24 * 60 * 60 }); // 1 year
  },

  /**
   * Get user preferences
   */
  getPreferences: () => {
    return CookieManager.get('user_preferences') || {
      theme: 'matrix_green',
      notifications: true,
      emailNotifications: true,
      language: 'en'
    };
  },

  /**
   * Update specific preference
   */
  updatePreference: (key, value) => {
    const prefs = PreferencesCookies.getPreferences();
    prefs[key] = value;
    PreferencesCookies.savePreferences(prefs);
  }
};

export default CookieManager;
