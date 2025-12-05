// ========================================
// ⌨️ TYPEWRITER EFFECT
// ========================================

class TypewriterEffect {
    constructor(element, texts, options = {}) {
        this.element = element;
        this.texts = Array.isArray(texts) ? texts : [texts];
        this.speed = options.speed || 80;
        this.deleteSpeed = options.deleteSpeed || 40;
        this.pauseTime = options.pauseTime || 2000;
        this.loop = options.loop !== false;
        
        this.currentTextIndex = 0;
        this.currentCharIndex = 0;
        this.isDeleting = false;
        this.isPaused = false;
        
        this.init();
    }
    
    init() {
        this.type();
    }
    
    type() {
        const currentText = this.texts[this.currentTextIndex];
        
        if (this.isDeleting) {
            // Remove character
            this.element.textContent = currentText.substring(0, this.currentCharIndex - 1);
            this.currentCharIndex--;
            
            if (this.currentCharIndex === 0) {
                this.isDeleting = false;
                this.currentTextIndex = (this.currentTextIndex + 1) % this.texts.length;
                setTimeout(() => this.type(), 500);
                return;
            }
        } else {
            // Add character
            this.element.textContent = currentText.substring(0, this.currentCharIndex + 1);
            this.currentCharIndex++;
            
            if (this.currentCharIndex === currentText.length) {
                if (this.loop && this.texts.length > 1) {
                    setTimeout(() => {
                        this.isDeleting = true;
                        this.type();
                    }, this.pauseTime);
                }
                return;
            }
        }
        
        const speed = this.isDeleting ? this.deleteSpeed : this.speed;
        setTimeout(() => this.type(), speed);
    }
}

// Initialize typewriter effect
document.addEventListener('DOMContentLoaded', () => {
    const typedTextElement = document.getElementById('typedText');
    if (typedTextElement) {
        const texts = [
            'Transforming Ideas Into Digital Reality',
            'Swiss Digital Excellence in Every Project',
            'Professional Development Solutions',
            'Your Vision, Our Expertise'
        ];
        
        new TypewriterEffect(typedTextElement, texts, {
            speed: 80,
            deleteSpeed: 40,
            pauseTime: 3000,
            loop: true
        });
    }
});

// Cursor blinking effect
document.addEventListener('DOMContentLoaded', () => {
    const cursor = document.createElement('span');
    cursor.className = 'cursor';
    cursor.textContent = '|';
    
    const typedTextElement = document.getElementById('typedText');
    if (typedTextElement) {
        typedTextElement.appendChild(cursor);
    }
});