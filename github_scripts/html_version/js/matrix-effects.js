// ========================================
// 💚 MATRIX RAIN EFFECT
// ========================================

class MatrixRain {
    constructor() {
        this.canvas = document.getElementById('matrix-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ019SOLUTIONS';
        this.charArray = this.chars.split('');
        this.fontSize = 14;
        this.columns = 0;
        this.drops = [];
        
        this.init();
        this.animate();
    }
    
    init() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.columns = Math.floor(this.canvas.width / this.fontSize);
        
        // Initialize drops
        this.drops = [];
        for (let i = 0; i < this.columns; i++) {
            this.drops[i] = 1;
        }
    }
    
    draw() {
        // Semi-transparent black background for fade effect
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Green text
        this.ctx.fillStyle = '#00ff00';
        this.ctx.font = `${this.fontSize}px 'JetBrains Mono', monospace`;
        
        for (let i = 0; i < this.drops.length; i++) {
            const text = this.charArray[Math.floor(Math.random() * this.charArray.length)];
            const x = i * this.fontSize;
            const y = this.drops[i] * this.fontSize;
            
            this.ctx.fillText(text, x, y);
            
            // Reset drop to top randomly
            if (y > this.canvas.height && Math.random() > 0.975) {
                this.drops[i] = 0;
            }
            
            this.drops[i]++;
        }
    }
    
    animate() {
        this.draw();
        setTimeout(() => this.animate(), 50);
    }
    
    resize() {
        this.init();
    }
}

// Initialize Matrix Rain
document.addEventListener('DOMContentLoaded', () => {
    const matrixRain = new MatrixRain();
    
    window.addEventListener('resize', () => {
        matrixRain.resize();
    });
});

// Matrix notification system
class MatrixNotification {
    constructor() {
        this.messages = [
            '◆ 019 SOLUTIONS ◆ Digital Architects of Tomorrow ◆ SWITZERLAND ◆',
            '>>> MATRIX ACTIVE >>> RENDERING FUTURE <<<',
            '019SOLUTIONS >>> DIGITAL ARCHITECTS OF TOMORROW <<<',
            '>>> SWITZERLAND >>> INNOVATION >>> 019 <<<'
        ];
        this.isVisible = false;
        this.init();
    }
    
    init() {
        // Create notification element
        this.notification = document.createElement('div');
        this.notification.className = 'matrix-notification';
        this.notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.9), rgba(59, 130, 246, 0.8));
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 10px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            font-weight: 600;
            z-index: 10000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(139, 92, 246, 0.3);
            max-width: 350px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        `;
        
        document.body.appendChild(this.notification);
        
        // Start notification cycle
        setTimeout(() => this.showNotification(), 5000);
    }
    
    showNotification() {
        if (this.isVisible) return;
        
        const message = this.messages[Math.floor(Math.random() * this.messages.length)];
        this.notification.textContent = message;
        this.notification.style.transform = 'translateX(0)';
        this.isVisible = true;
        
        // Hide after 10 seconds
        setTimeout(() => {
            this.notification.style.transform = 'translateX(100%)';
            this.isVisible = false;
            
            // Schedule next notification
            setTimeout(() => this.showNotification(), 30000);
        }, 10000);
    }
}

// Initialize Matrix Notification
document.addEventListener('DOMContentLoaded', () => {
    new MatrixNotification();
});