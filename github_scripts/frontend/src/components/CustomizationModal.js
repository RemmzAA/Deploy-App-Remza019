import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getCustomization, updateCustomization } from '../utils/licenseManager';
import './CustomizationModal.css';

const CustomizationModal = ({ isOpen, onClose, onSave }) => {
  const [customization, setCustomization] = useState({
    userName: 'REMZA019 Gaming',
    matrixColor: '#00ff00',
    textColor: '#00ff00',
    logoUrl: '/remza-logo.png'
  });

  useEffect(() => {
    if (isOpen) {
      const savedCustomization = getCustomization();
      setCustomization(savedCustomization);
    }
  }, [isOpen]);

  const handleSave = () => {
    updateCustomization(customization);
    if (onSave) {
      onSave(customization);
    }
    onClose();
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="customization-modal-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="customization-modal-content"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="customization-modal-header">
            <h2>🎨 Customization</h2>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>

          <div className="customization-modal-body">
            <div className="customization-field">
              <label>Username</label>
              <input
                type="text"
                value={customization.userName}
                onChange={(e) => setCustomization({...customization, userName: e.target.value})}
                placeholder="REMZA019 Gaming"
              />
            </div>

            <div className="customization-field">
              <label>Matrix Color</label>
              <input
                type="color"
                value={customization.matrixColor}
                onChange={(e) => setCustomization({...customization, matrixColor: e.target.value})}
              />
            </div>

            <div className="customization-field">
              <label>Text Color</label>
              <input
                type="color"
                value={customization.textColor}
                onChange={(e) => setCustomization({...customization, textColor: e.target.value})}
              />
            </div>

            <div className="customization-field">
              <label>Logo URL (optional)</label>
              <input
                type="text"
                value={customization.logoUrl}
                onChange={(e) => setCustomization({...customization, logoUrl: e.target.value})}
                placeholder="/remza-logo.png"
              />
            </div>
          </div>

          <div className="customization-modal-footer">
            <button className="cancel-btn" onClick={onClose}>Cancel</button>
            <button className="save-btn" onClick={handleSave}>Save Changes</button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default CustomizationModal;
