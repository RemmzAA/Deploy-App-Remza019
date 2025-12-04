import React from 'react';
import './Logo3D.css';

const Logo3D = ({ logoUrl = '/remza-logo.png', userName = 'REMZA019' }) => {
  // Use custom logo if provided, otherwise use default
  const displayLogo = logoUrl && logoUrl !== '/remza-logo.png' ? logoUrl : '/remza-logo.png';
  
  return (
    <div className="logo-3d-container">
      <div className="logo-3d-cube">
        <div className="cube-face cube-front">
          <img src={displayLogo} alt={userName} className="logo-img" />
        </div>
        <div className="cube-face cube-back">
          <img src={displayLogo} alt={userName} className="logo-img" />
        </div>
        <div className="cube-face cube-right">
          <img src={displayLogo} alt={userName} className="logo-img" />
        </div>
        <div className="cube-face cube-left">
          <img src={displayLogo} alt={userName} className="logo-img" />
        </div>
        <div className="cube-face cube-top">
          <img src={displayLogo} alt={userName} className="logo-img" />
        </div>
        <div className="cube-face cube-bottom">
          <img src={displayLogo} alt={userName} className="logo-img" />
        </div>
      </div>
      <div className="logo-glow-effect"></div>
    </div>
  );
};

export default Logo3D;
