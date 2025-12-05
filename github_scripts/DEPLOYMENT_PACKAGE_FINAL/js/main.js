// ========================================
// 019 SOLUTIONS - MAIN JAVASCRIPT
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 019 Solutions Website Loaded');
    
    // Initialize all components
    initLanguageSwitcher();
    initNavigation();
    initPortfolioFilter();
    initAdminPanel();
    initContactForm();
    initSmoothScrolling();
    initTypewriterEffect();
    
    // Start Matrix Rain Effect
    initMatrixRain();
});

// ========================================
// LANGUAGE SWITCHER
// ========================================
function initLanguageSwitcher() {
    const languageToggle = document.getElementById('languageToggle');
    const languageDropdown = document.getElementById('languageDropdown');
    const languageOptions = document.querySelectorAll('.modern-lang-option');
    
    if (!languageToggle || !languageDropdown) return;
    
    // Toggle dropdown
    languageToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        languageDropdown.classList.toggle('visible');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.modern-language-switcher')) {
            languageDropdown.classList.remove('visible');
        }
    });
    
    // Handle language selection
    languageOptions.forEach(option => {
        option.addEventListener('click', function() {
            const lang = this.dataset.lang;
            const flag = this.querySelector('span:first-child').textContent;
            const name = lang.toUpperCase();
            
            // Update button
            languageToggle.innerHTML = `
                <span>${flag}</span>
                <span>${name}</span>
                <span style="font-size: 0.7rem; opacity: 0.7;">▼</span>
            `;
            
            // Update active state
            languageOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            
            // Close dropdown
            languageDropdown.classList.remove('visible');
            
            console.log(`Language changed to: ${lang}`);
        });
    });
}

// ========================================
// NAVIGATION MENU
// ========================================
function initNavigation() {
    const menuContainer = document.getElementById('menuContainer');
    const menuToggle = document.getElementById('menuToggle');
    const navigationDropdown = document.getElementById('navigationDropdown');
    
    if (!menuContainer || !menuToggle || !navigationDropdown) return;
    
    // Toggle menu on hover
    menuContainer.addEventListener('mouseenter', function() {
        navigationDropdown.classList.add('visible');
        menuToggle.classList.add('active');
    });
    
    menuContainer.addEventListener('mouseleave', function() {
        navigationDropdown.classList.remove('visible');
        menuToggle.classList.remove('active');
    });
    
    // Handle navigation clicks
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('href');
            const element = document.querySelector(target);
            
            if (element) {
                element.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
            
            // Close mobile menu
            navigationDropdown.classList.remove('visible');
        });
    });
}

// ========================================
// PORTFOLIO FILTER
// ========================================
function initPortfolioFilter() {
    const filterButtons = document.querySelectorAll('.filter-button');
    const portfolioCards = document.querySelectorAll('.portfolio-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.dataset.filter;
            
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filter cards
            portfolioCards.forEach(card => {
                const category = card.dataset.category;
                
                if (filter === 'all' || category === filter) {
                    card.style.display = 'block';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100);
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
}

// ========================================
// ADMIN PANEL TABS
// ========================================
function initAdminPanel() {
    const adminTabs = document.querySelectorAll('.admin-nav-tab');
    
    adminTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Update active tab
            adminTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            const tabName = this.dataset.tab;
            console.log(`Admin tab switched to: ${tabName}`);
            
            // Here you can add logic to show/hide different admin content
            // For now, we'll just log the tab change
        });
    });
}

// ========================================
// CONTACT FORM
// ========================================
function initContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    if (!contactForm) return;
    
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());
        
        // Simple form validation
        const requiredFields = this.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.style.borderColor = '#ef4444';
                setTimeout(() => {
                    field.style.borderColor = '';
                }, 3000);
            }
        });
        
        if (isValid) {
            // Simulate form submission
            const submitBtn = this.querySelector('.form-submit-compact');
            const originalText = submitBtn.textContent;
            
            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;
            
            setTimeout(() => {
                submitBtn.textContent = 'Message Sent! ✓';
                submitBtn.style.background = 'linear-gradient(135deg, #059669, #047857)';
                
                // Reset form
                setTimeout(() => {
                    this.reset();
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                    submitBtn.style.background = '';
                }, 2000);
            }, 1000);
            
            console.log('Contact form submitted:', data);
        }
    });
}

// ========================================
// SMOOTH SCROLLING
// ========================================
function initSmoothScrolling() {
    // Handle all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            
            if (target) {
                const offsetTop = target.offsetTop - 80; // Account for fixed header
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ========================================
// TYPEWRITER EFFECT
// ========================================
function initTypewriterEffect() {
    const typedElement = document.querySelector('.typed-text');
    if (!typedElement) return;
    
    const text = "Transforming Ideas Into Digital Reality";
    const cursor = typedElement.querySelector('.cursor');
    let index = 0;
    
    // Clear existing text
    typedElement.textContent = '';
    if (cursor) typedElement.appendChild(cursor);
    
    function typeWriter() {
        if (index < text.length) {
            const textNode = document.createTextNode(text.charAt(index));
            if (cursor) {
                typedElement.insertBefore(textNode, cursor);
            } else {
                typedElement.appendChild(textNode);
            }
            index++;
            setTimeout(typeWriter, 80);
        }
    }
    
    // Start typing after a delay
    setTimeout(typeWriter, 2000);
}

// ========================================
// UTILITY FUNCTIONS
// ========================================
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Service button clicks
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('service-button')) {
        scrollToSection('contact');
        
        // Pre-fill service in contact form if available
        const serviceTitle = e.target.closest('.service-card').querySelector('.service-title');
        if (serviceTitle) {
            const serviceSelect = document.querySelector('.form-select-compact');
            if (serviceSelect) {
                const serviceName = serviceTitle.textContent;
                // Try to match service option
                const options = serviceSelect.querySelectorAll('option');
                options.forEach(option => {
                    if (option.textContent.includes(serviceName.split(' ')[0])) {
                        option.selected = true;
                    }
                });
            }
        }
    }
    
    // Handle payment method clicks
    if (e.target.closest('.payment-btn-footer')) {
        const paymentMethod = e.target.closest('.payment-btn-footer').dataset.method;
        console.log(`Payment method selected: ${paymentMethod}`);
        
        // You can add payment integration logic here
        alert(`${paymentMethod.charAt(0).toUpperCase() + paymentMethod.slice(1)} payment integration - Contact us for setup!`);
    }
});

// Contact button clicks in freelancer cards
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('contact-btn')) {
        scrollToSection('contact');
        
        // Pre-fill message
        const freelancerName = e.target.closest('.freelancer-card-modern').querySelector('.freelancer-name');
        if (freelancerName) {
            const textarea = document.querySelector('.form-textarea-compact');
            if (textarea) {
                textarea.value = `Hi, I'm interested in hiring ${freelancerName.textContent} for a project.`;
            }
        }
    }
});

console.log('🎯 019 Solutions JavaScript initialized successfully!');