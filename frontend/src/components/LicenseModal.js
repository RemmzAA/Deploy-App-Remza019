import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { activateFullLicense, getLicenseStatus } from '../utils/licenseManager';
import './LicenseModal.css';

const LicenseModal = ({ isOpen, onClose, onActivated }) => {
  const [licenseKey, setLicenseKey] = useState('');
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleActivate = async () => {
    if (!licenseKey.trim()) {
      setMessage('❌ Please enter a license key');
      setIsError(true);
      return;
    }

    setIsLoading(true);
    setMessage('🔄 Verifying license with server...');
    setIsError(false);

    try {
      const result = await activateFullLicense(licenseKey.trim().toUpperCase());
      
      setMessage(result.message);
      setIsError(!result.success);
      setIsLoading(false);

      if (result.success) {
        setTimeout(() => {
          if (onActivated) {
            onActivated();
          }
          onClose();
        }, 2000);
      }
    } catch (error) {
      setMessage('❌ Error activating license. Please try again.');
      setIsError(true);
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleActivate();
    }
  };

  const licenseStatus = getLicenseStatus();

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="license-modal-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="license-modal-container"
          initial={{ opacity: 0, scale: 0.8, y: 50 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: 50 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="license-modal-header">
            <h2 className="license-modal-title">
              {licenseStatus.type === 'TRIAL_EXPIRED' ? '⚠️ Trial Expired' : '🔑 Activate License'}
            </h2>
            <button className="license-modal-close" onClick={onClose}>✕</button>
          </div>

          {/* Content */}
          <div className="license-modal-content">
            {licenseStatus.type === 'TRIAL_EXPIRED' && (
              <div className="license-modal-warning">
                <p>Your 7-day trial has ended.</p>
                <p>Purchase a full license to continue using all features.</p>
              </div>
            )}

            <div className="license-modal-info">
              <h3>📦 What You Get:</h3>
              <ul>
                <li>✅ Lifetime access to all features</li>
                <li>✅ Full customization (colors, logo, name)</li>
                <li>✅ Your YouTube channel integration</li>
                <li>✅ Custom social media links</li>
                <li>✅ Priority support</li>
                <li>✅ Free updates</li>
              </ul>
            </div>

            <div className="license-modal-pricing">
              <div className="license-price-card">
                <span className="license-price">$49</span>
                <span className="license-price-label">one-time payment</span>
              </div>
            </div>

            <div className="license-modal-purchase">
              <h3>💳 How to Purchase:</h3>
              <ol>
                <li>Contact us: <a href="mailto:remza019@gmail.com">remza019@gmail.com</a></li>
                <li>Complete payment via Stripe/PayPal</li>
                <li>Receive your license key instantly</li>
                <li>Enter the key below to activate</li>
              </ol>
            </div>

            {/* License Key Input */}
            <div className="license-input-section">
              <label className="license-input-label">Enter Your License Key:</label>
              <input
                type="text"
                className="license-input"
                placeholder="FULL-XXXXX-XXXXX-XXXXX"
                value={licenseKey}
                onChange={(e) => setLicenseKey(e.target.value.toUpperCase())}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                maxLength={23}
              />
              <p className="license-input-hint">Format: FULL-XXXXX-XXXXX-XXXXX</p>
            </div>

            {/* Message */}
            {message && (
              <motion.div
                className={`license-message ${isError ? 'license-message-error' : 'license-message-success'}`}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                {message}
              </motion.div>
            )}

            {/* Actions */}
            <div className="license-modal-actions">
              <button
                className="license-btn license-btn-primary"
                onClick={handleActivate}
                disabled={isLoading || !licenseKey.trim()}
              >
                {isLoading ? '🔄 Activating...' : '🔑 Activate License'}
              </button>
              <button
                className="license-btn license-btn-secondary"
                onClick={onClose}
                disabled={isLoading}
              >
                Cancel
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default LicenseModal;
