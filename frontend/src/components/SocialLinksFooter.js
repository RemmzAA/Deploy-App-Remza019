import React from 'react';
import { motion } from 'framer-motion';
import './SocialLinksFooter.css';

const SocialLinksFooter = ({ links }) => {
  if (!links) return null;

  const socialButtons = [
    { key: 'discord', icon: '💬', label: 'Discord', color: '#5865F2' },
    { key: 'youtube', icon: '📺', label: 'YouTube', color: '#FF0000' },
    { key: 'twitch', icon: '🎮', label: 'Twitch', color: '#9146FF' },
    { key: 'twitter', icon: '🐦', label: 'Twitter', color: '#1DA1F2' },
    { key: 'instagram', icon: '📸', label: 'Instagram', color: '#E4405F' },
    { key: 'tiktok', icon: '🎵', label: 'TikTok', color: '#000000' }
  ];

  const activeSocials = socialButtons.filter(social => links[social.key]);

  if (activeSocials.length === 0) return null;

  return (
    <div className="social-links-footer">
      <motion.h3 
        className="social-title"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        🌐 Connect With Us
      </motion.h3>
      <div className="social-buttons-grid">
        {activeSocials.map((social, index) => (
          <motion.a
            key={social.key}
            href={links[social.key]}
            target="_blank"
            rel="noopener noreferrer"
            className="social-button"
            style={{ '--social-color': social.color }}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.1 * index }}
            whileHover={{ scale: 1.1, y: -5 }}
            whileTap={{ scale: 0.95 }}
          >
            <span className="social-icon">{social.icon}</span>
            <span className="social-label">{social.label}</span>
          </motion.a>
        ))}
      </div>
    </div>
  );
};

export default SocialLinksFooter;
