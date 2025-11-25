import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './LicenseActivation.css';

const LicenseActivation = () => {
  const [licenseKey, setLicenseKey] = useState('');
  const [licenseStatus, setLicenseStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showActivation, setShowActivation] = useState(false);

  const API_URL = process.env.REACT_APP_BACKEND_URL;

  // Check license status on mount
  useEffect(() => {
    checkLicenseStatus();
  }, []);

  const checkLicenseStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/license/status`);
      if (response.ok) {
        const data = await response.json();
        setLicenseStatus(data);
      }
    } catch (error) {
      console.error('Failed to check license status:', error);
    }
  };

  const handleActivate = async () => {
    if (!licenseKey.trim()) {
      alert('⚠️ Molim unesite aktivacioni ključ!');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/license/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ license_key: licenseKey })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        alert(`🎉 Licenca uspešno aktivirana!\n\nTip: ${data.license.license_type}\nIsteče: ${data.license.expires_at || 'Nikada'}`);
        setLicenseStatus(data.license);
        setLicenseKey('');
        setShowActivation(false);
      } else {
        alert(`❌ Aktivacija nije uspela:\n${data.detail || data.message || 'Nepoznata greška'}`);
      }
    } catch (error) {
      alert(`❌ Greška pri aktivaciji:\n${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('sr-Latn-RS', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getDaysRemaining = (expiresAt) => {
    if (!expiresAt) return null;
    const now = new Date();
    const expiry = new Date(expiresAt);
    const diffTime = expiry - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  return (
    <>
      {/* License Status Badge */}
      <div className="license-badge" onClick={() => setShowActivation(true)}>
        {licenseStatus ? (
          <>
            {licenseStatus.is_active ? (
              <span className="license-active">
                🔑 {licenseStatus.license_type === 'TRIAL' ? 'Trial' : 'Licensed'}
              </span>
            ) : (
              <span className="license-inactive">🔒 Not Activated</span>
            )}
          </>
        ) : (
          <span className="license-inactive">🔒 Check License</span>
        )}
      </div>

      {/* Activation Modal */}
      <AnimatePresence>
        {showActivation && (
          <motion.div
            className="license-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowActivation(false)}
          >
            <motion.div
              className="license-modal"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <button className="close-modal" onClick={() => setShowActivation(false)}>✕</button>

              <h2 className="license-title">🔑 Aktivacija Licence</h2>

              {/* Current Status */}
              {licenseStatus && licenseStatus.is_active ? (
                <div className="license-status-card active">
                  <h3>✅ Licenca Aktivna</h3>
                  <div className="status-details">
                    <p><strong>Tip:</strong> {licenseStatus.license_type === 'TRIAL' ? 'Probna (7 dana)' : 'Puna Licenca'}</p>
                    <p><strong>Ključ:</strong> <code>{licenseStatus.license_key}</code></p>
                    {licenseStatus.activated_at && (
                      <p><strong>Aktivirana:</strong> {formatDate(licenseStatus.activated_at)}</p>
                    )}
                    {licenseStatus.expires_at && (
                      <>
                        <p><strong>Ističe:</strong> {formatDate(licenseStatus.expires_at)}</p>
                        {getDaysRemaining(licenseStatus.expires_at) !== null && (
                          <p className="days-remaining">
                            <strong>Preostalo dana:</strong> {getDaysRemaining(licenseStatus.expires_at)}
                          </p>
                        )}
                      </>
                    )}
                  </div>
                </div>
              ) : (
                <div className="license-status-card inactive">
                  <h3>🔒 Licenca Nije Aktivirana</h3>
                  <p>Unesite aktivacioni ključ da otključate sve funkcije aplikacije.</p>
                </div>
              )}

              {/* Activation Form */}
              <div className="activation-form">
                <label>Aktivacioni Ključ:</label>
                <input
                  type="text"
                  className="license-input"
                  placeholder="TRIAL-XXXXX-XXXXX-XXXXX"
                  value={licenseKey}
                  onChange={(e) => setLicenseKey(e.target.value.toUpperCase())}
                  disabled={loading}
                />

                <button
                  className="activate-btn"
                  onClick={handleActivate}
                  disabled={loading || !licenseKey.trim()}
                >
                  {loading ? '⏳ Aktiviranje...' : '🔓 Aktiviraj Licencu'}
                </button>
              </div>

              {/* Info Section */}
              <div className="license-info">
                <h4>ℹ️ O Licensi</h4>
                <ul>
                  <li><strong>Trial Licenca:</strong> 7 dana besplatnog korišćenja</li>
                  <li><strong>Puna Licenca:</strong> Neograničen pristup svim funkcijama</li>
                  <li><strong>Format Ključa:</strong> XXX-XXXXX-XXXXX-XXXXX</li>
                </ul>
              </div>

              {/* Generate Trial Button */}
              {!licenseStatus || !licenseStatus.is_active ? (
                <button
                  className="trial-btn"
                  onClick={async () => {
                    try {
                      const response = await fetch(`${API_URL}/api/license/generate`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ license_type: 'TRIAL' })
                      });
                      const data = await response.json();
                      if (data.license_key) {
                        setLicenseKey(data.license_key);
                        alert(`🎉 Trial ključ generisan!\n\n${data.license_key}\n\nKliknite "Aktiviraj Licencu" da ga aktivirate.`);
                      }
                    } catch (error) {
                      alert('❌ Greška pri generisanju trial ključa');
                    }
                  }}
                >
                  🎁 Generiši Trial Ključ (7 dana)
                </button>
              ) : null}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default LicenseActivation;
