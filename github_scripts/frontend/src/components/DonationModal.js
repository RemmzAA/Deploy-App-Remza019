import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '../i18n/LanguageContext';
import './DonationModal.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const DonationModal = ({ isOpen, onClose }) => {
  const { t } = useLanguage();
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [customAmount, setCustomAmount] = useState('');
  const [donorName, setDonorName] = useState('');
  const [donorEmail, setDonorEmail] = useState('');
  const [message, setMessage] = useState('');
  const [packages, setPackages] = useState([]);
  const [recentDonations, setRecentDonations] = useState([]);
  const [donationStats, setDonationStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load donation packages and stats
  useEffect(() => {
    if (isOpen) {
      loadDonationData();
    }
  }, [isOpen]);

  const loadDonationData = async () => {
    try {
      // Load packages
      const packagesRes = await fetch(`${BACKEND_URL}/api/donations/packages`);
      const packagesData = await packagesRes.json();
      
      if (packagesData.packages) {
        const packageArray = Object.entries(packagesData.packages).map(([id, pkg]) => ({
          id,
          ...pkg
        }));
        setPackages(packageArray);
      }

      // Load recent donations
      const donationsRes = await fetch(`${BACKEND_URL}/api/donations/recent?limit=5`);
      const donationsData = await donationsRes.json();
      setRecentDonations(donationsData.donations || []);

      // Load stats
      const statsRes = await fetch(`${BACKEND_URL}/api/donations/stats`);
      const statsData = await statsRes.json();
      setDonationStats(statsData);

    } catch (err) {
      console.error('Failed to load donation data:', err);
    }
  };

  const handlePackageSelect = (pkg) => {
    setSelectedPackage(pkg);
    if (pkg.id !== 'custom') {
      setCustomAmount('');
    }
  };

  const handleDonation = async () => {
    if (!selectedPackage) {
      setError('Please select a donation package');
      return;
    }

    if (selectedPackage.id === 'custom' && (!customAmount || parseFloat(customAmount) < 1)) {
      setError('Custom amount must be at least $1.00');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const amount = selectedPackage.id === 'custom' ? parseFloat(customAmount) : selectedPackage.amount;
      
      const response = await fetch(`${BACKEND_URL}/api/donations/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          package_id: selectedPackage.id,
          amount: selectedPackage.id === 'custom' ? amount : undefined,
          donor_name: donorName || 'Anonymous',
          donor_email: donorEmail || '',
          message: message || '',
          origin_url: window.location.origin
        }),
      });

      const data = await response.json();

      if (data.success && data.checkout_url) {
        // Redirect to Stripe checkout
        window.location.href = data.checkout_url;
      } else {
        throw new Error(data.detail || 'Failed to create checkout session');
      }

    } catch (err) {
      console.error('Donation error:', err);
      setError(err.message || 'Failed to process donation. Please try again.');
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="donation-modal-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="donation-modal"
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="donation-modal-header">
            <h2>{t('supportTitle')}</h2>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>

          <div className="donation-modal-content">
            {/* Donation Disclaimer - PROMINENT */}
            <div className="donation-disclaimer">
              {t('donationDisclaimer')}
            </div>

            {/* Donation Stats */}
            {donationStats && (
              <div className="donation-stats-banner">
                <div className="stat-item">
                  <span className="stat-label">{t('totalRaised')}</span>
                  <span className="stat-value">
                    ${donationStats.total_amount?.toFixed(2) || '0.00'}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">{t('totalSupporters')}</span>
                  <span className="stat-value">{donationStats.total_donations || 0}</span>
                </div>
              </div>
            )}

            {/* Donation Packages */}
            <div className="donation-packages">
              <h3>{t('chooseLevel')}</h3>
              <div className="packages-grid">
                {packages.map((pkg) => (
                  <motion.div
                    key={pkg.id}
                    className={`package-card ${selectedPackage?.id === pkg.id ? 'selected' : ''}`}
                    onClick={() => handlePackageSelect(pkg)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="package-icon">{pkg.icon}</div>
                    <div className="package-name">{pkg.name}</div>
                    <div className="package-amount">
                      {pkg.id === 'custom' ? t('yourAmount') : `$${pkg.amount}`}
                    </div>
                    <div className="package-description">{pkg.description}</div>
                    {pkg.features && (
                      <ul className="package-features">
                        {pkg.features.map((feature, idx) => (
                          <li key={idx}>{feature}</li>
                        ))}
                      </ul>
                    )}
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Custom Amount Input */}
            {selectedPackage?.id === 'custom' && (
              <motion.div
                className="custom-amount-input"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
              >
                <label>{t('enterAmount')}</label>
                <input
                  type="number"
                  min="1"
                  step="0.01"
                  value={customAmount}
                  onChange={(e) => setCustomAmount(e.target.value)}
                  placeholder={t('enterAmount')}
                />
              </motion.div>
            )}

            {/* Donor Information */}
            {selectedPackage && (
              <motion.div
                className="donor-info"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
              >
                <h3>{t('yourInfo')}</h3>
                <div className="form-group">
                  <label>{t('name')}</label>
                  <input
                    type="text"
                    value={donorName}
                    onChange={(e) => setDonorName(e.target.value)}
                    placeholder={t('namePlaceholder')}
                  />
                </div>
                <div className="form-group">
                  <label>{t('email')}</label>
                  <input
                    type="email"
                    value={donorEmail}
                    onChange={(e) => setDonorEmail(e.target.value)}
                    placeholder={t('emailForReceipt')}
                  />
                </div>
                <div className="form-group">
                  <label>{t('message')}</label>
                  <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder={t('messagePlaceholder')}
                    rows="3"
                  />
                </div>
              </motion.div>
            )}

            {/* Error Message */}
            {error && (
              <div className="error-message">
                ⚠️ {error}
              </div>
            )}

            {/* Donate Button */}
            {selectedPackage && (
              <motion.button
                className="donate-btn"
                onClick={handleDonation}
                disabled={loading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {loading ? `⏳ ${t('processing')}` : `💚 ${t('donate')} ${selectedPackage.id === 'custom' && customAmount ? `$${customAmount}` : selectedPackage.id !== 'custom' ? `$${selectedPackage.amount}` : ''}`}
              </motion.button>
            )}

            {/* Recent Donations */}
            {recentDonations.length > 0 && (
              <div className="recent-donations">
                <h3>{t('recentSupporters')}</h3>
                <div className="donations-list">
                  {recentDonations.map((donation, idx) => (
                    <div key={idx} className="donation-item">
                      <div className="donor-info">
                        <span className="donor-name">{donation.donor_name}</span>
                        <span className="donation-amount">${donation.amount}</span>
                      </div>
                      {donation.message && (
                        <div className="donation-message">"{donation.message}"</div>
                      )}
                      <div className="donation-date">{donation.date}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Secure Payment Notice */}
            <div className="secure-notice">
              <span className="secure-icon">🔒</span>
              <span>{t('securePayment')}</span>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default DonationModal;
