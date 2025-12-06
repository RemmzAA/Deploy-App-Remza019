import React, { useEffect, useState } from 'react';
import './Logo3D.css';

const Logo3D = ({ logoUrl = '/remza-logo.png', userName = 'REMZA019', licenseType = 'NONE' }) => {
  // ALWAYS show "R" watermark cube (removed premium/NONE logic)
  return (
    <div className="logo-3d-container">
      {/* Always show 3D rotating "R" */}
      <div className="logo-3d-cube watermark">
          <div className="cube-face cube-front">
            <div className="letter-r">R</div>
          </div>
          <div className="cube-face cube-back">
            <div className="letter-r">R</div>
          </div>
          <div className="cube-face cube-right">
            <div className="letter-r">R</div>
          </div>
          <div className="cube-face cube-left">
            <div className="letter-r">R</div>
          </div>
          <div className="cube-face cube-top">
            <div className="letter-r">R</div>
          </div>
          <div className="cube-face cube-bottom">
            <div className="letter-r">R</div>
          </div>
        </div>
      ) : (
        // Premium: Custom logo (shown for PREMIUM users)
        <div className="logo-3d-cube premium">
          <div className="cube-face cube-front">
            <img src={logoUrl} alt={userName} className="logo-img" />
          </div>
          <div className="cube-face cube-back">
            <img src={logoUrl} alt={userName} className="logo-img" />
          </div>
          <div className="cube-face cube-right">
            <img src={logoUrl} alt={userName} className="logo-img" />
          </div>
          <div className="cube-face cube-left">
            <img src={logoUrl} alt={userName} className="logo-img" />
          </div>
          <div className="cube-face cube-top">
            <img src={logoUrl} alt={userName} className="logo-img" />
          </div>
          <div className="cube-face cube-bottom">
            <img src={logoUrl} alt={userName} className="logo-img" />
          </div>
        </div>
      )}
      <div className="logo-glow-effect"></div>
      {showWatermark && (
        <div className="watermark-badge">
          <span>🔒 Premium Required</span>
        </div>
      )}
    </div>
  );
};

export default Logo3D;
