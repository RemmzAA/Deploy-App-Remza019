import React, { useEffect, useRef } from 'react';

const MatrixRain = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Matrix characters - including REMZA019 and GAMING
    const characters = '01REMZA019GAMINGREMZA019GAMING01900190190190190190190190190190190190190'.split('');
    
    const fontSize = 18;
    const columns = Math.floor(canvas.width / fontSize);
    const drops = new Array(columns).fill(0);

    // Animation loop
    const animate = () => {
      // Semi-transparent black background for trailing effect
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Green text
      ctx.fillStyle = '#10b981';
      ctx.font = `${fontSize}px 'Courier New', monospace`;
      ctx.textAlign = 'center';

      for (let i = 0; i < drops.length; i++) {
        // Random character
        const char = characters[Math.floor(Math.random() * characters.length)];
        
        // Draw character
        const x = i * fontSize + fontSize / 2;
        const y = drops[i] * fontSize;
        
        ctx.fillText(char, x, y);
        
        // Randomly reset drop to top
        if (y > canvas.height && Math.random() > 0.98) {
          drops[i] = 0;
        }
        
        // Move drop down
        drops[i]++;
      }
    };

    // Start animation
    const intervalId = setInterval(animate, 50);

    return () => {
      clearInterval(intervalId);
      window.removeEventListener('resize', resizeCanvas);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 1,
        opacity: 0.6,
        pointerEvents: 'none'
      }}
    />
  );
};

export default MatrixRain;