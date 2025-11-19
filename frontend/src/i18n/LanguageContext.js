import React, { createContext, useState, useContext, useEffect } from 'react';
import { getTranslation } from './translations';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  // Get language from localStorage or default to Serbian
  const [language, setLanguage] = useState(() => {
    const saved = localStorage.getItem('remza019_language');
    return saved || 'sr'; // Default to Serbian
  });

  // Save to localStorage when language changes
  useEffect(() => {
    localStorage.setItem('remza019_language', language);
    console.log(`🌍 Language changed to: ${language}`);
  }, [language]);

  const t = (key) => getTranslation(language, key);

  const toggleLanguage = () => {
    // Cycle through EN → SR → DE
    setLanguage(prev => {
      if (prev === 'en') return 'sr';
      if (prev === 'sr') return 'de';
      return 'en';
    });
  };

  const value = {
    language,
    setLanguage,
    toggleLanguage,
    t
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};
