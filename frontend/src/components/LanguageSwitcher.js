import React from 'react';
import { motion } from 'framer-motion';
import { useLanguage } from '../i18n/LanguageContext';
import './LanguageSwitcher.css';

const LanguageSwitcher = () => {
  const { language, toggleLanguage } = useLanguage();

  // Get flag and code based on current language
  const getLanguageDisplay = () => {
    switch(language) {
      case 'en': return { flag: '🇬🇧', code: 'EN' };
      case 'sr': return { flag: '🇷🇸', code: 'SR' };
      case 'de': return { flag: '🇩🇪', code: 'DE' };
      default: return { flag: '🇷🇸', code: 'SR' };
    }
  };

  const display = getLanguageDisplay();

  return (
    <motion.div 
      className="language-switcher-floating"
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <button 
        className="lang-switch-btn"
        onClick={toggleLanguage}
        aria-label="Switch Language"
        title="EN → SR → DE"
      >
        <span className="lang-flag">
          {display.flag}
        </span>
        <span className="lang-code">
          {display.code}
        </span>
      </button>
    </motion.div>
  );
};

export default LanguageSwitcher;
