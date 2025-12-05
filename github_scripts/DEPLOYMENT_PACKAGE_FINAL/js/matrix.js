// ========================================
// MATRIX RAIN EFFECT
// ========================================

function initMatrixRain() {
    const canvas = document.getElementById('matrixCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Matrix characters (mix of Latin, numbers, and some special chars)
    const matrixChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()_+-=[]{}|;':\",./<>?`~";
    const chars = matrixChars.split('');
    
    const fontSize = 14;
    const columns = canvas.width / fontSize;
    
    // Array to store the y position of each column
    const drops = [];
    
    // Initialize drops
    for (let x = 0; x < columns; x++) {
        drops[x] = Math.floor(Math.random() * canvas.height / fontSize);
    }
    
    function draw() {
        // Create fade effect
        ctx.fillStyle = 'rgba(10, 10, 10, 0.04)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Set text properties
        ctx.fillStyle = '#10b981'; // Green color
        ctx.font = fontSize + 'px monospace';
        
        // Draw characters
        for (let i = 0; i < drops.length; i++) {
            // Random character
            const text = chars[Math.floor(Math.random() * chars.length)];
            
            // Draw character
            ctx.fillStyle = '#10b981';
            
            // Add some variation in green shades
            const alpha = Math.random() * 0.8 + 0.2;
            ctx.fillStyle = `rgba(16, 185, 129, ${alpha})`;
            
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            
            // Reset drop to top randomly
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            
            // Move drop down
            drops[i]++;
        }
    }
    
    // Animation loop
    function animate() {
        draw();
        requestAnimationFrame(animate);
    }
    
    // Start animation
    animate();
    
    console.log('🌧️ Matrix rain effect initialized');
}

// Additional matrix effects for enhanced visual appeal
function addMatrixGlow() {
    const canvas = document.getElementById('matrixCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Add glow effect
    ctx.shadowColor = '#10b981';
    ctx.shadowBlur = 10;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMatrixRain);
} else {
    initMatrixRain();
}