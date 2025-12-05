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

    // Matrix characters - more 0s and 1s for authentic matrix effect
    const characters = '01010101010101010101010101010101REMZA019GAMING01010101010101010101'.split('');
    
    const fontSize = 14;  // Povećano za bolje čitljivost
    const columns = Math.floor(canvas.width / fontSize);
    const drops = new Array(columns).fill(0);

    // Initialize random starting positions
    for (let i = 0; i < drops.length; i++) {
      drops[i] = Math.random() * canvas.height / fontSize;
    }

    // Animation loop
    const animate = () => {
      // Solid black background - NO GRID LINES
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';  // Smanjeno za duži trail
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Get custom matrix color from CSS variable
      const matrixColor = getComputedStyle(document.documentElement)
        .getPropertyValue('--matrix-color').trim() || '#00ff00';
      
      // Convert hex to RGB for dynamic opacity
      const hexToRgb = (hex) => {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
          r: parseInt(result[1], 16),
          g: parseInt(result[2], 16),
          b: parseInt(result[3], 16)
        } : { r: 0, g: 255, b: 0 };
      };
      
      const rgb = hexToRgb(matrixColor);
      
      ctx.font = `${fontSize}px 'Courier New', monospace`;
      ctx.textAlign = 'center';

      for (let i = 0; i < drops.length; i++) {
        // Random character (više 0 i 1)
        const char = characters[Math.floor(Math.random() * characters.length)];
        
        // Draw character
        const x = i * fontSize + fontSize / 2;
        const y = drops[i] * fontSize;
        
        // Add some brightness variation with custom color
        const brightness = 0.3 + Math.random() * 0.7;
        ctx.fillStyle = `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${brightness})`;
        
        ctx.fillText(char, x, y);
        
        // Randomly reset drop to top
        if (y > canvas.height && Math.random() > 0.99) {
          drops[i] = 0;
        }
        
        // Move drop down - više kontinuirano
        if (Math.random() > 0.1) {  // 90% šanse da se pomeri
          drops[i]++;
        }
      }
    };

    // Start animation - brži refresh za fluid efekat
    const intervalId = setInterval(animate, 50);  // Vraćeno na 50ms

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
        opacity: 0.6,  // Povećano za jasniji efekat
        pointerEvents: 'none',
        backgroundColor: '#000000'  // SOLID BLACK BACKGROUND
      }}
    />
  );
};

export default MatrixRain;