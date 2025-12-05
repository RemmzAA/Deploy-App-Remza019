// ========================================
// 🚀 MAIN APPLICATION LOGIC
// ========================================

class App {
    constructor() {
        this.currentFilter = 'All';
        this.init();
    }
    
    async init() {
        await this.loadServices();
        await this.loadPortfolio();
        this.initContactForm();
        this.initAnimations();
        this.initUtilityFunctions();
        
        console.log('✅ 019 Solutions HTML app initialized successfully');
    }
    
    async loadServices() {
        try {
            const services = await api.fetchServices();
            this.renderServices(services);
        } catch (error) {
            console.error('Error loading services:', error);
        }
    }
    
    renderServices(services) {
        const servicesGrid = document.getElementById('servicesGrid');
        if (!servicesGrid) return;
        
        servicesGrid.innerHTML = services.map(service => `
            <div class="service-card matrix-card">
                <div class="service-icon">${service.icon}</div>
                <h3 class="service-title">${service.name}</h3>
                <p class="service-description">${service.description}</p>
                
                <ul class="service-features">
                    ${service.features.map(feature => `
                        <li class="feature-item">
                            <span class="feature-check">✓</span>
                            ${feature}
                        </li>
                    `).join('')}
                </ul>
                
                <button class="service-button matrix-button" onclick="handleServiceContact('${service.id}')">
                    Get Quote
                </button>
            </div>
        `).join('');
    }
    
    async loadPortfolio() {
        try {
            const projects = await api.fetchProjects();
            this.renderPortfolio(projects);
        } catch (error) {
            console.error('Error loading portfolio:', error);
        }
    }
    
    renderPortfolio(projects) {
        const portfolioGrid = document.getElementById('portfolioGrid');
        if (!portfolioGrid) return;
        
        portfolioGrid.innerHTML = projects.map(project => `
            <div class="portfolio-card matrix-card" data-category="${project.category}">
                <div class="project-image">
                    <div class="project-placeholder" style="background: linear-gradient(135deg, #8b5cf6, #3b82f6); display: flex; align-items: center; justify-content: center; height: 250px; color: white; font-size: 3rem;">
                        ${this.getCategoryIcon(project.category)}
                    </div>
                    <div class="project-overlay">
                        <a href="${project.live_demo}" class="project-link matrix-button" target="_blank">
                            View Live
                        </a>
                    </div>
                </div>
                
                <div class="project-content">
                    <div class="project-category">${project.category}</div>
                    <h3 class="project-title">${project.title}</h3>
                    <p class="project-description">${project.description}</p>
                    
                    <div class="project-tech">
                        ${project.technologies.map(tech => `
                            <span class="tech-tag">${tech}</span>
                        `).join('')}
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    getCategoryIcon(category) {
        const icons = {
            'Fintech': '📈',
            'Gaming': '🎮',
            'Tourism': '🌊',
            'Real Estate': '🏢',
            'E-commerce': '🛒',
            'Healthcare': '🏥'
        };
        return icons[category] || '💼';
    }
    
    initContactForm() {
        const contactForm = document.getElementById('contactForm');
        if (!contactForm) return;
        
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(contactForm);
            const data = Object.fromEntries(formData.entries());
            
            const submitButton = contactForm.querySelector('.submit-button');
            const submitMessage = document.getElementById('submitMessage');
            
            // Show loading state
            submitButton.textContent = 'Sending...';
            submitButton.disabled = true;
            
            try {
                await api.submitContact(data);
                
                // Show success message
                submitMessage.textContent = '✅ Message sent successfully!';
                submitMessage.className = 'submit-message success';
                submitMessage.style.display = 'block';
                
                // Reset form
                contactForm.reset();
                
            } catch (error) {
                // Show error message
                submitMessage.textContent = '❌ Error sending message. Please try again.';
                submitMessage.className = 'submit-message error';
                submitMessage.style.display = 'block';
            } finally {
                // Reset button
                submitButton.textContent = 'Send Message';
                submitButton.disabled = false;
                
                // Hide message after 5 seconds
                setTimeout(() => {
                    submitMessage.style.display = 'none';
                }, 5000);
            }
        });
    }
    
    initAnimations() {
        // Initialize letter animations
        const solutionLetters = document.querySelectorAll('.solution-letter');
        solutionLetters.forEach((letter, index) => {
            letter.style.animationDelay = `${index * 0.2}s`;
        });
        
        // Initialize scroll animations
        this.initScrollAnimations();
    }
    
    initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);
        
        // Observe elements for scroll animations
        document.querySelectorAll('.matrix-card, .service-card, .portfolio-card').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(50px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });
    }
    
    initUtilityFunctions() {
        // Make functions globally available
        window.handleServiceContact = this.handleServiceContact.bind(this);
        window.filterPortfolio = this.filterPortfolio.bind(this);
        window.copyToClipboard = this.copyToClipboard.bind(this);
    }
    
    handleServiceContact(serviceId) {
        // Scroll to contact section
        scrollToSection('#contact');
        
        // Pre-fill service selection
        setTimeout(() => {
            const serviceSelect = document.querySelector('select[name="service_interest"]');
            if (serviceSelect) {
                serviceSelect.value = serviceId;
            }
        }, 500);
    }
    
    filterPortfolio(category) {
        this.currentFilter = category;
        
        // Update filter buttons
        document.querySelectorAll('.filter-button').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeButton = [...document.querySelectorAll('.filter-button')].find(btn => 
            btn.textContent.trim() === category
        );
        if (activeButton) {
            activeButton.classList.add('active');
        }
        
        // Filter portfolio items
        const portfolioCards = document.querySelectorAll('.portfolio-card');
        portfolioCards.forEach(card => {
            const cardCategory = card.getAttribute('data-category');
            
            if (category === 'All' || cardCategory === category) {
                card.style.display = 'block';
                card.style.opacity = '0';
                card.style.transform = 'scale(0.8)';
                
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'scale(1)';
                }, 100);
            } else {
                card.style.opacity = '0';
                card.style.transform = 'scale(0.8)';
                
                setTimeout(() => {
                    card.style.display = 'none';
                }, 300);
            }
        });
    }
    
    copyToClipboard(text, type) {
        navigator.clipboard.writeText(text).then(() => {
            // Show success notification
            const notification = document.createElement('div');
            notification.textContent = `✅ ${type} address copied to clipboard!`;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, #10b981, #06b6d4);
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 10px;
                font-family: 'Space Grotesk', sans-serif;
                font-weight: 600;
                z-index: 10000;
                animation: slideInRight 0.3s ease;
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => {
                    document.body.removeChild(notification);
                }, 300);
            }, 3000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            alert(`${type} address: ${text}`);
        });
    }
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new App();
});