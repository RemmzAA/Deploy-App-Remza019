import React, { useEffect, useState } from 'react';
import './Logo3D.css';

const Logo3D = ({ logoUrl = '/remza-logo.png', userName = 'REMZA019', licenseType = 'NONE' }) => {
  // Always show the custom logo in 3D rotating cube
  
  return (
    <div className="logo-3d-container">
      {/* Always show custom logo in 3D rotating cube */}
      <div className={`logo-3d-cube ${licenseType === 'PREMIUM' ? 'premium' : ''}`}>
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
      <div className="logo-glow-effect"></div>
    </div>
  );
};

export default Logo3D;
