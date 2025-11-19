import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getLicenseStatus, getRemainingTrialDays } from '../utils/licenseManager';
import './TrialStatus.css';

const TrialStatus = ({ onExpired }) => {
  const [licenseStatus, setLicenseStatus] = useState(null);
  const [remainingDays, setRemainingDays] = useState(null);

  useEffect(() => {
    // Check license status
    const status = getLicenseStatus();
    setLicenseStatus(status);
    
    if (status.type === 'TRIAL') {
      const days = getRemainingTrialDays();
      setRemainingDays(days);
      
      // Notify parent if expired
      if (days === 0 && onExpired) {
        onExpired();
      }
    }
    
    // Recheck every hour
    const interval = setInterval(() => {
      const updatedStatus = getLicenseStatus();
      setLicenseStatus(updatedStatus);
      
      if (updatedStatus.type === 'TRIAL') {
        const days = getRemainingTrialDays();
        setRemainingDays(days);
        
        if (days === 0 && onExpired) {
          onExpired();
        }
      }
    }, 1000 * 60 * 60); // Check every hour
    
    return () => clearInterval(interval);
  }, [onExpired]);

  if (!licenseStatus) {
    return null;
  }

  // Don't show anything for full license
  if (licenseStatus.type === 'FULL') {
    return null;
  }

  // Trial expired - critical warning
  if (licenseStatus.type === 'TRIAL_EXPIRED') {
    return (
      <motion.div
        className="trial-status trial-expired"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <span className="trial-icon">⚠️</span>
        <span className="trial-text">TRIAL EXPIRED</span>
        <span className="trial-action">Purchase License</span>
      </motion.div>
    );
  }

  // Trial active - show remaining days
  if (licenseStatus.type === 'TRIAL') {
    const urgentWarning = remainingDays <= 2;
    
    return (
      <motion.div
        className={`trial-status trial-active ${urgentWarning ? 'trial-urgent' : ''}`}
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <span className="trial-icon">⏳</span>
        <span className="trial-text">
          TRIAL: {remainingDays} {remainingDays === 1 ? 'DAY' : 'DAYS'} LEFT
        </span>
      </motion.div>
    );
  }

  return null;
};

export default TrialStatus;
