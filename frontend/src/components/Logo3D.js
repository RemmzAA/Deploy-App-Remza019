import React from 'react';
import './Logo3D.css';

const Logo3D = () => {
  return (
    <div className="logo-3d-container">
      <div className="logo-3d-cube">
        <div className="cube-face cube-front">
          <img src="/remza-logo.png" alt="REMZA" className="logo-img" />
        </div>
        <div className="cube-face cube-back">
          <img src="/remza-logo.png" alt="REMZA" className="logo-img" />
        </div>
        <div className="cube-face cube-right">
          <img src="/remza-logo.png" alt="REMZA" className="logo-img" />
        </div>
        <div className="cube-face cube-left">
          <img src="/remza-logo.png" alt="REMZA" className="logo-img" />
        </div>
        <div className="cube-face cube-top">
          <img src="/remza-logo.png" alt="REMZA" className="logo-img" />
        </div>
        <div className="cube-face cube-bottom">
          <img src="/remza-logo.png" alt="REMZA" className="logo-img" />
        </div>
      </div>
      <div className="logo-glow-effect"></div>
    </div>
  );
};

export default Logo3D;
