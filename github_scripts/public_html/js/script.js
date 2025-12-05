// Enhanced MATRIX BACKGROUND EFFECT + BLACK HORIZONTAL CODES
function createMatrixEffect() {
    const matrixBg = document.getElementById('matrix-bg');
    const characters = '01ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const specialWords = ['0DEVETNAST', '0NINETEEN', '019', 'SOLUTIONS', 'MATRIX', 'CODE', 'DIGITAL', 'FINTECH', 'GAMING', 'TOURISM', 'BLOCKCHAIN'];
    const blackCodeChars = '█▓▒░▄▀■□▪▫◘◙☻☺♠♣♥♦•◘○●◯◉⦿⦾⚫⚪⬛⬜▰▱╬╪┼┬┴┤├▲►▼◄★☆♦♠♣♥';
    const intenseCodes = '████████▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒░░░░░░░░■■■■■■■■□□□□□□□□';
    
    // Intense Black Code Rain Function
    function createIntenseBlackRain() {
        for (let i = 0; i < 6; i++) {
            setTimeout(() => {
                const blackLine = document.createElement('div');
                blackLine.className = 'black-code-line';
                if (Math.random() < 0.4) blackLine.className += ' inverted';
                
                blackLine.style.top = Math.random() * 100 + '%';
                
                let content = '';
                for (let j = 0; j < 140; j++) {
                    if (Math.random() < 0.2) {
                        content += '█019█';
                    } else {
                        content += intenseCodes[Math.floor(Math.random() * intenseCodes.length)];
                    }
                }
                
                blackLine.textContent = content;
                document.body.appendChild(blackLine);
                
                setTimeout(() => {
                    if (blackLine.parentNode) {
                        blackLine.parentNode.removeChild(blackLine);
                    }
                }, 6000);
            }, i * 150);
        }
    }
    
    function createMatrixColumn() {
        const column = document.createElement('div');
        column.className = 'matrix-column';
        column.style.left = Math.random() * 100 + '%';
        column.style.animationDuration = (Math.random() * 3 + 2) + 's';
        column.style.animationDelay = Math.random() * 2 + 's';
        
        // Decide if this should be a special column
        const isSpecial = Math.random() < 0.25; // 25% chance for special words
        
        if (isSpecial) {
            column.className += ' special';
            const specialWord = specialWords[Math.floor(Math.random() * specialWords.length)];
            
            // Create the special word with some regular characters
            let content = '';
            for (let i = 0; i < Math.random() * 15 + 10; i++) {
                if (i === Math.floor(Math.random() * 18 + 6)) {
                    content += specialWord + '\n';
                } else {
                    content += characters[Math.floor(Math.random() * characters.length)] + '\n';
                }
            }
            column.textContent = content;
        } else {
            // Regular matrix column
            let content = '';
            const length = Math.random() * 30 + 20;
            for (let i = 0; i < length; i++) {
                content += characters[Math.floor(Math.random() * characters.length)] + '\n';
            }
            column.textContent = content;
        }
        
        // Animation
        column.style.animation = `matrixFall ${Math.random() * 5 + 4}s linear infinite`;
        
        matrixBg.appendChild(column);
        
        // Remove column after animation
        setTimeout(() => {
            if (column.parentNode) {
                column.parentNode.removeChild(column);
            }
        }, 12000);
    }
    
    // BLACK HORIZONTAL CODE FUNCTION - ENHANCED
    function createBlackCodeLine() {
        const blackLine = document.createElement('div');
        blackLine.className = 'black-code-line';
        
        // Random chance for different styles
        const styleRandom = Math.random();
        if (styleRandom < 0.25) {
            blackLine.className += ' special-019';
        } else if (styleRandom < 0.6) {
            blackLine.className += ' inverted';
        }
        
        // Random vertical position (cover more of the screen)
        blackLine.style.top = Math.random() * 95 + 2 + '%';
        
        // Create black code content with more variety
        let blackContent = '';
        const lineLength = Math.random() * 100 + 80; // 80-180 characters
        
        for (let i = 0; i < lineLength; i++) {
            if (Math.random() < 0.18) { // 18% chance for special words
                const blackSpecials = [
                    '▓▓▓019▓▓▓', 
                    '░░MATRIX░░', 
                    '▀▀CODE▀▀', 
                    '■DIGITAL■', 
                    '●CYBER●',
                    '◘SOLUTIONS◘',
                    '▪FINTECH▪',
                    '◙GAMING◙',
                    '⚫BLOCKCHAIN⚫',
                    '▰▰AI▰▰',
                    '★SWITZERLAND★'
                ];
                blackContent += blackSpecials[Math.floor(Math.random() * blackSpecials.length)] + ' ';
                i += 12; // Skip some iterations to avoid overcrowding
            } else {
                blackContent += blackCodeChars[Math.floor(Math.random() * blackCodeChars.length)];
            }
        }
        
        blackLine.textContent = blackContent;
        
        // Add to body
        document.body.appendChild(blackLine);
        
        // Remove after animation completes
        setTimeout(() => {
            if (blackLine.parentNode) {
                blackLine.parentNode.removeChild(blackLine);
            }
        }, 6000);
    }
    
    // Special 019 Black Code Lines
    function createSpecial019Line() {
        const blackLine = document.createElement('div');
        blackLine.className = 'black-code-line special-019';
        blackLine.style.top = Math.random() * 90 + 5 + '%';
        
        const special019Messages = [
            '◆◆◆ 019 SOLUTIONS - DIGITAL ARCHITECTS OF TOMORROW ◆◆◆ █▓▒░ MATRIX CODE ACTIVATED ░▒▓█',
            '▰▰▰ SWITZERLAND BASED • WORLDWIDE REACH • PREMIUM QUALITY ▰▰▰ ◘◘◘ CONTACT: contact@019solutions.com ◘◘◘',
            '★★★ FULL-STACK • GAMING • AI • BLOCKCHAIN • E-COMMERCE ★★★ ▓▓▓ www.019solutions.com ▓▓▓',
            '●●● TRANSFORMING IDEAS INTO DIGITAL REALITY ●●● ░░░ Discord Community Available ░░░'
        ];
        
        const randomMessage = special019Messages[Math.floor(Math.random() * special019Messages.length)];
        blackLine.textContent = randomMessage;
        
        document.body.appendChild(blackLine);
        
        setTimeout(() => {
            if (blackLine.parentNode) {
                blackLine.parentNode.removeChild(blackLine);
            }
        }, 5000);
    }
    
    // Create matrix keyframes
    const style = document.createElement('style');
    style.textContent = `
        @keyframes matrixFall {
            0% {
                transform: translateY(-100vh);
                opacity: 1;
            }
            100% {
                transform: translateY(100vh);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Create vertical matrix columns periodically
    setInterval(createMatrixColumn, 80);
    
    // Create horizontal black code lines frequently
    setInterval(createBlackCodeLine, 1000); // Every 1 second
    setInterval(createSpecial019Line, 5000); // Special 019 lines every 5 seconds
    setInterval(createIntenseBlackRain, 12000); // Intense rain every 12 seconds
    
    // Initial burst of vertical columns
    for (let i = 0; i < 40; i++) {
        setTimeout(createMatrixColumn, i * 60);
    }
    
    // Initial black code lines - very active
    setTimeout(createBlackCodeLine, 300);
    setTimeout(createBlackCodeLine, 800);
    setTimeout(createIntenseBlackRain, 1500);
    setTimeout(createSpecial019Line, 2500);
    setTimeout(createBlackCodeLine, 3200);
    setTimeout(createBlackCodeLine, 4000);
    setTimeout(createSpecial019Line, 5000);
    setTimeout(createBlackCodeLine, 6000);
    setTimeout(createIntenseBlackRain, 7500);
}

// Enhanced cursor following effect with Matrix style
document.addEventListener('mousemove', function(e) {
    const x = e.clientX;
    const y = e.clientY;
    document.body.style.setProperty('--mouse-x', x + 'px');
    document.body.style.setProperty('--mouse-y', y + 'px');
});

// Mobile Navigation Toggle
const navToggle = document.getElementById('nav-toggle');
const navMenu = document.getElementById('nav-menu');

if (navToggle && navMenu) {
    navToggle.addEventListener('click', function() {
        navToggle.classList.toggle('active');
        navMenu.classList.toggle('active');
    });

    // Close mobile menu when clicking on links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navToggle.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offsetTop = target.offsetTop - 70; // Account for fixed navigation
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    });
});

// Counter Animation for Stats
function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    const speed = 200; // Animation speed

    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const count = parseInt(counter.innerText);
        const inc = target / speed;

        if (count < target) {
            counter.innerText = Math.ceil(count + inc);
            setTimeout(() => animateCounters(), 1);
        } else {
            counter.innerText = target;
        }
    });
}

// Scroll reveal animation
function revealOnScroll() {
    const reveals = document.querySelectorAll('.service-card, .portfolio-card, .about-stat');
    
    reveals.forEach(element => {
        const windowHeight = window.innerHeight;
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150;
        
        if (elementTop < windowHeight - elementVisible) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
}

// Initialize scroll reveal styles
document.addEventListener('DOMContentLoaded', function() {
    const elements = document.querySelectorAll('.service-card, .portfolio-card, .about-stat');
    elements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });
});

// Service button interactions
document.querySelectorAll('.service-btn').forEach(button => {
    button.addEventListener('click', function() {
        const serviceType = this.getAttribute('data-service');
        
        // Scroll to contact form
        const contactSection = document.getElementById('contact');
        const offsetTop = contactSection.offsetTop - 70;
        window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
        });
        
        // Pre-fill the service dropdown after scroll
        setTimeout(() => {
            const serviceSelect = document.getElementById('service');
            if (serviceSelect && serviceType) {
                serviceSelect.value = serviceType;
                
                // Focus on name input
                const nameInput = document.getElementById('name');
                if (nameInput) {
                    nameInput.focus();
                }
            }
        }, 1000);
    });
});

// Contact form handling
document.getElementById('contactForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const name = formData.get('name');
    const email = formData.get('email');
    const company = formData.get('company');
    const service = formData.get('service');
    const message = formData.get('message');
    const budget = formData.get('budget');
    
    // Create mailto link
    const subject = `New Project Inquiry - ${service}`;
    const body = `Name: ${name}
Email: ${email}
Company: ${company || 'Not specified'}
Service: ${service}
Budget: ${budget}
Message: ${message}

Best regards,
${name}`;
    
    const encodedSubject = encodeURIComponent(subject);
    const encodedBody = encodeURIComponent(body);
    const mailtoLink = `mailto:contact@019solutions.com?subject=${encodedSubject}&body=${encodedBody}`;
    
    // Show success message
    const submitBtn = this.querySelector('.submit-btn');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Message Sent! Opening Email...';
    submitBtn.style.background = 'linear-gradient(135deg, #4ecdc4, #00ff41)';
    
    // Open mailto link
    window.location.href = mailtoLink;
    
    // Reset button after 3 seconds
    setTimeout(() => {
        submitBtn.textContent = originalText;
        submitBtn.style.background = 'linear-gradient(135deg, #ff6b6b, #4ecdc4)';
        this.reset();
    }, 3000);
});

// Typewriter effect for hero subtitle
function typeWriter() {
    const element = document.getElementById('typewriter');
    const text = 'Transforming Ideas Into Digital Reality';
    let i = 0;
    
    function type() {
        if (i < text.length) {
            element.textContent = text.substring(0, i + 1);
            i++;
            setTimeout(type, 100);
        } else {
            // Remove cursor after typing is complete
            setTimeout(() => {
                element.style.borderRight = 'none';
            }, 1000);
        }
    }
    
    // Start typing after a delay
    setTimeout(() => {
        element.textContent = '';
        type();
    }, 1000);
}

// Page Performance Optimization
function optimizePerformance() {
    // Lazy loading for portfolio images
    const images = document.querySelectorAll('img[loading="lazy"]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.src || img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    }
    
    // Preload critical resources
    const criticalLinks = [
        'css/style.css',
        'js/script.js'
    ];
    
    criticalLinks.forEach(href => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = href;
        link.as = href.includes('.css') ? 'style' : 'script';
        document.head.appendChild(link);
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Matrix effect
    createMatrixEffect();
    
    // Initialize typewriter effect
    typeWriter();
    
    // Start counter animation after a delay
    setTimeout(() => {
        animateCounters();
    }, 2000);
    
    // Initialize performance optimizations
    optimizePerformance();
    
    // Add scroll event listeners
    window.addEventListener('scroll', revealOnScroll);
    
    // Initial scroll reveal check
    revealOnScroll();
});

// Matrix notification system (periodic notifications)
function createMatrixNotification() {
    const notification = document.createElement('div');
    notification.className = 'matrix-notification';
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.9);
        color: #00ff41;
        padding: 15px 20px;
        border-radius: 10px;
        border: 1px solid #00ff41;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        z-index: 10000;
        animation: slideIn 0.5s ease-out;
        max-width: 300px;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
    `;
    
    const messages = [
        '◆ 019 SOLUTIONS ◆\nDigital Architects of Tomorrow\nSWITZERLAND',
        '◆ MATRIX ACTIVATED ◆\nFull-Stack Development\nReady for Deployment',
        '◆ SYSTEM ONLINE ◆\nAI Integration Available\nContact for Projects',
        '◆ CODE COMPILED ◆\nSwiss Quality Standards\nwww.019solutions.com'
    ];
    
    notification.textContent = messages[Math.floor(Math.random() * messages.length)];
    
    // Add slide-in animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    // Remove notification after 8 seconds
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.5s ease-out reverse';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 500);
    }, 8000);
}

// Show matrix notification every 30 seconds
setInterval(createMatrixNotification, 30000);

// Show first notification after 5 seconds
setTimeout(createMatrixNotification, 5000);