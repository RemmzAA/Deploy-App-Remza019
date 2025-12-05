import React from 'react';
import { getCustomization } from '../utils/licenseManager';
import './SocialLinks.css';

const SocialLinks = () => {
  const customization = getCustomization();
  const { socialLinks, discordLink } = customization;

  const hasSocialLinks = socialLinks && (
    socialLinks.twitter || 
    socialLinks.instagram || 
    socialLinks.twitch || 
    socialLinks.tiktok ||
    discordLink
  );

  if (!hasSocialLinks) return null;

  return (
    <div className="social-links-container">
      <h3>Connect With Me</h3>
      <div className="social-icons">
        {socialLinks.twitter && (
          <a 
            href={`https://twitter.com/${socialLinks.twitter.replace('@', '')}`}
            target="_blank"
            rel="noopener noreferrer"
            className="social-icon twitter"
            title="Twitter/X"
          >
            <span>𝕏</span>
          </a>
        )}
        {socialLinks.instagram && (
          <a 
            href={`https://instagram.com/${socialLinks.instagram.replace('@', '')}`}
            target="_blank"
            rel="noopener noreferrer"
            className="social-icon instagram"
            title="Instagram"
          >
            📷
          </a>
        )}
        {socialLinks.twitch && (
          <a 
            href={`https://twitch.tv/${socialLinks.twitch}`}
            target="_blank"
            rel="noopener noreferrer"
            className="social-icon twitch"
            title="Twitch"
          >
            📺
          </a>
        )}
        {socialLinks.tiktok && (
          <a 
            href={`https://tiktok.com/@${socialLinks.tiktok.replace('@', '')}`}
            target="_blank"
            rel="noopener noreferrer"
            className="social-icon tiktok"
            title="TikTok"
          >
            🎵
          </a>
        )}
        {discordLink && (
          <a 
            href={discordLink.startsWith('http') ? discordLink : `https://${discordLink}`}
            target="_blank"
            rel="noopener noreferrer"
            className="social-icon discord"
            title="Discord"
          >
            💬
          </a>
        )}
      </div>
    </div>
  );
};

export default SocialLinks;
