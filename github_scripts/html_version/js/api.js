// ========================================
// 🌐 API INTEGRATION
// ========================================

class API {
    constructor() {
        this.baseURL = 'http://localhost:8001/api';
        this.services = [];
        this.projects = [];
    }
    
    async fetchServices() {
        try {
            const response = await fetch(`${this.baseURL}/services`);
            if (!response.ok) throw new Error('Failed to fetch services');
            this.services = await response.json();
            return this.services;
        } catch (error) {
            console.error('Error fetching services:', error);
            return this.getDefaultServices();
        }
    }
    
    async fetchProjects() {
        try {
            const response = await fetch(`${this.baseURL}/projects`);
            if (!response.ok) throw new Error('Failed to fetch projects');
            this.projects = await response.json();
            return this.projects;
        } catch (error) {
            console.error('Error fetching projects:', error);
            return this.getDefaultProjects();
        }
    }
    
    async submitContact(formData) {
        try {
            const response = await fetch(`${this.baseURL}/contact`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) throw new Error('Failed to submit form');
            return await response.json();
        } catch (error) {
            console.error('Error submitting contact form:', error);
            throw error;
        }
    }
    
    getDefaultServices() {
        return [
            {
                id: 'full-stack',
                name: 'Full-Stack Development',
                description: 'Complete web applications from frontend to backend with modern technologies.',
                features: ['React & Node.js', 'Database Design', 'API Development', '24/7 Support'],
                icon: '🔧',
                price_range: '$2,000-$15,000'
            },
            {
                id: 'ecommerce',
                name: 'E-Commerce Solutions',
                description: 'Professional online stores with payment integration and inventory management.',
                features: ['Payment Integration', 'Inventory Management', 'Order Processing', 'Analytics'],
                icon: '🛒',
                price_range: '$3,000-$20,000'
            },
            {
                id: 'mobile',
                name: 'Mobile Development',
                description: 'Native and cross-platform mobile applications for iOS and Android.',
                features: ['iOS & Android', 'Cross-platform', 'App Store Deployment', 'Push Notifications'],
                icon: '📱',
                price_range: '$5,000-$25,000'
            },
            {
                id: 'ai',
                name: 'AI Integration',
                description: 'Intelligent features powered by machine learning and artificial intelligence.',
                features: ['Machine Learning', 'Natural Language Processing', 'Computer Vision', 'Automation'],
                icon: '🤖',
                price_range: '$2,500-$20,000'
            },
            {
                id: 'consulting',
                name: 'Technical Consulting',
                description: 'Expert advice on technology choices, architecture, and best practices.',
                features: ['Architecture Review', 'Technology Selection', 'Performance Optimization', 'Security Audit'],
                icon: '💡',
                price_range: '$500-$3,000'
            },
            {
                id: 'gaming',
                name: 'Gaming Solutions',
                description: 'Game development and gaming platform solutions with modern technologies.',
                features: ['Game Development', 'Multiplayer Systems', 'Analytics', 'Monetization'],
                icon: '🎮',
                price_range: '$1,500-$10,000'
            }
        ];
    }
    
    getDefaultProjects() {
        return [
            {
                id: 'trading-demo',
                title: 'Trading Intelligence Platform',
                description: 'Advanced trading platform with real-time market data and AI-powered insights.',
                image: '/images/trading-demo.jpg',
                technologies: ['React', 'Node.js', 'WebSocket', 'Chart.js'],
                category: 'Fintech',
                live_demo: '/demo/trading'
            },
            {
                id: 'gaming-demo',
                title: 'Remza019 Gaming Website',
                description: 'Professional gaming community platform with streaming integration.',
                image: '/images/remza019-gaming.jpg',
                technologies: ['React', 'Express', 'Socket.io', 'MongoDB'],
                category: 'Gaming',
                live_demo: '/demo/gaming'
            },
            {
                id: 'tourism-demo',
                title: 'Adriatic Dreams Tourism',
                description: 'Beautiful tourism booking platform for coastal destinations.',
                image: '/images/adriatic-dreams.jpg',
                technologies: ['React', 'Node.js', 'Stripe', 'MongoDB'],
                category: 'Tourism',
                live_demo: '/demo/tourism'
            },
            {
                id: 'apartments-demo',
                title: 'Berlin Apartment Booking',
                description: 'Modern apartment rental platform with advanced search and booking.',
                image: '/images/berlin-apartments.jpg',
                technologies: ['React', 'FastAPI', 'PostgreSQL', 'Redis'],
                category: 'Real Estate',
                live_demo: '/demo/apartments'
            }
        ];
    }
}

// Initialize API
const api = new API();