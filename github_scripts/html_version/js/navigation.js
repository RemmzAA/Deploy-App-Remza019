// ========================================
// 🧭 NAVIGATION FUNCTIONALITY
// ========================================

class Navigation {
    constructor() {
        this.menuToggle = document.getElementById('menuToggle');
        this.navigationMenu = document.getElementById('navigationMenu');
        this.langToggle = document.getElementById('langToggle');
        this.langDropdown = document.getElementById('langDropdown');
        this.isMenuOpen = false;
        this.isLangOpen = false;
        
        this.init();
    }
    
    init() {
        // Menu toggle functionality
        if (this.menuToggle) {
            this.menuToggle.addEventListener('click', () => this.toggleMenu());
        }
        
        // Language toggle functionality
        if (this.langToggle) {
            this.langToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleLanguageDropdown();
            });
        }
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.navigation-dropdown') && this.isMenuOpen) {
                this.closeMenu();
            }
            if (!e.target.closest('.modern-language-switcher') && this.isLangOpen) {
                this.closeLangDropdown();
            }
        });
        
        // Close menu when clicking nav items
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', () => this.closeMenu());
        });
        
        // Smooth scroll for navigation
        this.initSmoothScroll();
    }
    
    toggleMenu() {
        this.isMenuOpen = !this.isMenuOpen;
        
        if (this.isMenuOpen) {
            this.openMenu();
        } else {
            this.closeMenu();
        }
    }
    
    openMenu() {
        this.menuToggle.classList.add('active');
        this.navigationMenu.classList.add('active');
        this.navigationMenu.style.display = 'block';
        this.isMenuOpen = true;
    }
    
    closeMenu() {
        this.menuToggle.classList.remove('active');
        this.navigationMenu.classList.remove('active');
        setTimeout(() => {
            this.navigationMenu.style.display = 'none';
        }, 300);
        this.isMenuOpen = false;
    }
    
    toggleLanguageDropdown() {
        this.isLangOpen = !this.isLangOpen;
        
        if (this.isLangOpen) {
            this.langDropdown.style.display = 'block';
            this.langToggle.querySelector('.dropdown-arrow').textContent = '▲';
        } else {
            this.closeLangDropdown();
        }
    }
    
    closeLangDropdown() {
        this.langDropdown.style.display = 'none';
        this.langToggle.querySelector('.dropdown-arrow').textContent = '▼';
        this.isLangOpen = false;
    }
    
    initSmoothScroll() {
        // Add smooth scrolling to all navigation links
        document.querySelectorAll('a[href^="#"], button[onclick*="scrollToSection"]').forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href') || link.getAttribute('onclick')?.match(/#[^'"]*/)?.[0];
                if (href && href.startsWith('#')) {
                    e.preventDefault();
                    this.scrollToSection(href);
                }
            });
        });
    }
    
    scrollToSection(targetId) {
        const target = document.querySelector(targetId);
        if (target) {
            const navHeight = document.querySelector('.clean-navigation').offsetHeight;
            const targetPosition = target.offsetTop - navHeight - 20;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    }
}

// Language switcher functionality
class LanguageSwitcher {
    constructor() {
        this.currentLang = 'en';
        this.languages = {
            en: { name: 'English', flag: '🇬🇧', code: 'EN' },
            de: { name: 'Deutsch', flag: '🇩🇪', code: 'DE' },
            sr: { name: 'Srpski', flag: '🇷🇸', code: 'SR' }
        };
        
        this.translations = {
            en: {
                'hero.tagline': 'Transforming Ideas Into Digital Reality',
                'services.title': 'Our Services',
                'services.subtitle': 'Professional solutions for your business',
                'portfolio.title': 'Our Portfolio',
                'portfolio.subtitle': 'Real projects with real results',
                'contact.title': 'Get In Touch',
                'contact.subtitle': 'Ready to start your project?'
            },
            de: {
                'hero.tagline': 'Ideen in Digitale Realität Verwandeln',
                'services.title': 'Unsere Dienstleistungen',
                'services.subtitle': 'Professionelle Lösungen für Ihr Unternehmen',
                'portfolio.title': 'Unser Portfolio',
                'portfolio.subtitle': 'Echte Projekte mit echten Ergebnissen',
                'contact.title': 'Kontakt Aufnehmen',
                'contact.subtitle': 'Bereit, Ihr Projekt zu starten?'
            },
            sr: {
                'hero.tagline': 'Pretvaranje Ideja u Digitalnu Stvarnost',
                'services.title': 'Naše Usluge',
                'services.subtitle': 'Profesionalna rešenja za vaš biznis',
                'portfolio.title': 'Naš Portfolio',
                'portfolio.subtitle': 'Pravi projekti sa pravim rezultatima',
                'contact.title': 'Kontaktirajte Nas',
                'contact.subtitle': 'Spremni da pokrenete projekat?'
            }
        };
    }
    
    changeLanguage(langCode) {
        if (!this.languages[langCode]) return;
        
        this.currentLang = langCode;
        const lang = this.languages[langCode];
        
        // Update toggle button
        const langToggle = document.getElementById('langToggle');
        if (langToggle) {
            langToggle.querySelector('.current-flag').textContent = lang.flag;
            langToggle.querySelector('.current-lang-code').textContent = lang.code;
        }
        
        // Update active state in dropdown
        document.querySelectorAll('.modern-lang-option').forEach(option => {
            option.classList.remove('active');
            const indicator = option.querySelector('.active-indicator');
            if (indicator) indicator.remove();
        });
        
        const activeOption = document.querySelector(`[onclick="changeLanguage('${langCode}')"]`);
        if (activeOption) {
            activeOption.classList.add('active');
            const indicator = document.createElement('span');
            indicator.className = 'active-indicator';
            indicator.textContent = '✓';
            activeOption.appendChild(indicator);
        }
        
        // Update translations
        this.updateTranslations();
        
        // Close dropdown
        const navigation = new Navigation();
        navigation.closeLangDropdown();
        
        console.log(`✅ Language changed to: ${langCode}`);
    }
    
    updateTranslations() {
        const translations = this.translations[this.currentLang];
        if (!translations) return;
        
        // Update translatable elements
        Object.keys(translations).forEach(key => {
            const elements = document.querySelectorAll(`[data-translate="${key}"]`);
            elements.forEach(element => {
                element.textContent = translations[key];
            });
        });
    }
}

// Global functions
function scrollToSection(targetId) {
    const navigation = new Navigation();
    navigation.scrollToSection(targetId);
}

function changeLanguage(langCode) {
    const langSwitcher = new LanguageSwitcher();
    langSwitcher.changeLanguage(langCode);
}

// Initialize navigation
document.addEventListener('DOMContentLoaded', () => {
    new Navigation();
    new LanguageSwitcher();
});