import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// SUBTLE MATRIX BACKGROUND COMPONENT - PROFESSIONAL VERSION
const MatrixBackground = () => {
  useEffect(() => {
    // Only add subtle cursor tracking and minimal footer effects
    
    // Enhanced cursor following (keep this - it's subtle and cool)
    const handleMouseMove = (e) => {
      document.body.style.setProperty('--mouse-x', e.clientX + 'px');
      document.body.style.setProperty('--mouse-y', e.clientY + 'px');
    };
    document.addEventListener('mousemove', handleMouseMove);

    // Neon Gamer notifications with orange and purple theme
    function createFooterNotification() {
      // Check if notification already exists
      if (document.querySelector('.matrix-footer-notification')) return;
      
      const notification = document.createElement('div');
      notification.className = 'matrix-footer-notification';
      
      // Gamer-style notification content with variety
      const gamerNotifications = [
        {
          matrix: '019',
          text: 'System Online',
          location: 'CH'
        },
        {
          matrix: 'CODE',
          text: 'Level Up Ready',
          location: 'PWR'
        },
        {
          matrix: 'NEON',
          text: 'Matrix Active',
          location: 'GFX'
        },
        {
          matrix: 'GAME',
          text: 'Innovation Mode',
          location: 'DEV'
        },
        {
          matrix: 'CYBER',
          text: 'Solutions Live',
          location: 'NET'
        }
      ];
      
      const randomNotification = gamerNotifications[Math.floor(Math.random() * gamerNotifications.length)];
      
      notification.innerHTML = `
        <span class="matrix-text">${randomNotification.matrix}</span>
        <span class="notification-text">${randomNotification.text}</span>
        <span class="matrix-text">${randomNotification.location}</span>
      `;
      
      // Add to body with neon gamer styling
      document.body.appendChild(notification);
      
      // Auto-remove after neon fade animation completes (10.5 seconds total)
      setTimeout(() => {
        if (notification.parentNode) {
          notification.remove();
        }
      }, 11000);
    }

    // Show neon gamer notifications with gaming intervals
    const notificationInterval = setInterval(createFooterNotification, 25000); // Every 25 seconds for gamer feel
    
    // Show initial notification after shorter delay for immediate neon impact
    setTimeout(createFooterNotification, 6000);

    // Cleanup
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      clearInterval(notificationInterval);
    };
  }, []);

  return null; // No background overlay
};

// Hero Section with animated typing effect
const Hero = () => {
  const [typedText, setTypedText] = useState('');
  const fullText = 'Transforming Ideas Into Digital Reality';
  
  useEffect(() => {
    let i = 0;
    const typeInterval = setInterval(() => {
      if (i < fullText.length) {
        setTypedText(fullText.slice(0, i + 1));
        i++;
      } else {
        clearInterval(typeInterval);
      }
    }, 100);
    
    return () => clearInterval(typeInterval);
  }, []);

  return (
    <section className="hero-section">
      <div className="hero-background"></div>
      <div className="hero-content">
        <div className="hero-logo">
          <div className="company-logo"></div>
          <div className="logo-glow"></div>
        </div>
        <h1 className="hero-title">
          <span className="brand-name">019</span>
          <span className="brand-solutions">SOLUTIONS</span>
        </h1>
        <div className="typing-container">
          <h2 className="typing-text">{typedText}<span className="cursor">|</span></h2>
        </div>
        <div className="signature-tagline">
          <div className="tagline-code">// WHERE CODE MEETS CREATIVITY</div>
          <div className="tagline-main">DIGITAL ARCHITECTS OF TOMORROW</div>
          <div className="tagline-binary">01001001 01001110 01001110 01001111 01010110 01000001 01010100 01001001 01001111 01001110</div>
        </div>
        <p className="hero-subtitle">
          Premium Web Development • Gaming Solutions • AI Innovation • Digital Transformation
        </p>
        <div className="hero-stats">
          <div className="stat">
            <span className="stat-number">50+</span>
            <span className="stat-label">Projects</span>
          </div>
          <div className="stat">
            <span className="stat-number">35+</span>
            <span className="stat-label">Happy Clients</span>
          </div>
          <div className="stat">
            <span className="stat-number">5+</span>
            <span className="stat-label">Years Experience</span>
          </div>
        </div>
        <div className="hero-buttons">
          <button className="btn-primary" onClick={() => document.getElementById('contact').scrollIntoView({behavior: 'smooth'})}>
            START YOUR PROJECT - FREE CONSULTATION
          </button>
          <button className="btn-secondary" onClick={() => document.getElementById('portfolio').scrollIntoView({behavior: 'smooth'})}>
            VIEW SUCCESS STORIES
          </button>
        </div>
        <div className="hero-guarantee">
          <div className="guarantee-badge">
            100% SATISFACTION GUARANTEE<br/>
            FREE REVISION UNTIL PERFECT<br/>
            DELIVERY ON TIME OR MONEY BACK
          </div>
        </div>
      </div>
      <div className="hero-particles"></div>
    </section>
  );
};

// Services Section
const Services = () => {
  const [services, setServices] = useState([]);

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const response = await axios.get(`${API}/services`);
        setServices(response.data);
      } catch (error) {
        console.error('Error fetching services:', error);
      }
    };
    fetchServices();
  }, []);

  return (
    <section id="services" className="services-section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Our Services</h2>
          <p className="section-subtitle">Professional solutions for every digital need</p>
        </div>
        <div className="services-grid">
          {services.map((service, index) => (
            <div key={service.id} className="service-card" style={{animationDelay: `${index * 0.2}s`}}>
              <div className="service-icon">{service.icon}</div>
              <h3 className="service-title">{service.name}</h3>
              <p className="service-description">{service.description}</p>
              <ul className="service-features">
                {service.features.map((feature, idx) => (
                  <li key={idx}>{feature}</li>
                ))}
              </ul>
              <div className="service-price">{service.price_range}</div>
              <button 
                className="service-btn"
                onClick={() => {
                  // Scroll to contact
                  document.getElementById('contact').scrollIntoView({behavior: 'smooth'});
                  // Pre-fill service dropdown after scroll completes
                  setTimeout(() => {
                    const serviceSelect = document.querySelector('select[name="service_interest"]');
                    if (serviceSelect) {
                      // Map service names to select options
                      const serviceMap = {
                        'Full-Stack Development': 'full-stack',
                        'Responsive Design': 'responsive',
                        'E-commerce Solutions': 'ecommerce',
                        'Performance Optimization': 'performance',
                        'Gaming Solutions': 'gaming',
                        'AI Integration': 'ai'
                      };
                      const optionValue = serviceMap[service.name];
                      if (optionValue) {
                        serviceSelect.value = optionValue;
                      }
                    }
                  }, 800);
                }}
              >
                Learn More
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Portfolio Section
const Portfolio = () => {
  const [projects, setProjects] = useState([]);
  const [activeFilter, setActiveFilter] = useState('All');

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await axios.get(`${API}/projects`);
        setProjects(response.data);
      } catch (error) {
        console.error('Error fetching projects:', error);
      }
    };
    fetchProjects();
  }, []);

  const categories = ['All', ...new Set(projects.map(project => project.category))];
  const filteredProjects = activeFilter === 'All' 
    ? projects 
    : projects.filter(project => project.category === activeFilter);

  return (
    <section id="portfolio" className="portfolio-section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Our Portfolio</h2>
          <p className="section-subtitle">Showcasing our expertise across industries</p>
        </div>
        
        <div className="portfolio-filters">
          {categories.map(category => (
            <button 
              key={category}
              className={`filter-btn ${activeFilter === category ? 'active' : ''}`}
              onClick={() => setActiveFilter(category)}
            >
              {category}
            </button>
          ))}
        </div>

        <div className="portfolio-grid">
          {filteredProjects.map((project, index) => (
            <div key={project.id} className="portfolio-card" style={{animationDelay: `${index * 0.15}s`}}>
              <div className="portfolio-image">
                <img src={project.image} alt={project.title} />
                <div className="portfolio-overlay">
                  <div className="portfolio-links">
                    <a href={project.live_demo} target="_blank" rel="noopener noreferrer" className="portfolio-link">
                      View Live
                    </a>
                  </div>
                </div>
              </div>
              <div className="portfolio-content">
                <div className="portfolio-category">{project.category}</div>
                <h3 className="portfolio-title">{project.title}</h3>
                <p className="portfolio-description">{project.description}</p>
                <div className="portfolio-technologies">
                  {project.technologies.map((tech, idx) => (
                    <span key={idx} className="tech-tag">{tech}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Pricing Section
const Pricing = () => {
  const pricingPlans = [
    {
      name: "STARTUP PACKAGE",
      price: "€2,500",
      popular: false,
      features: [
        "✅ Professional Website Design",
        "✅ Mobile Responsive Layout", 
        "✅ Contact Forms & SEO Setup",
        "✅ 3 Months Free Maintenance",
        "✅ Social Media Integration",
        "⚡ 2 Week Delivery"
      ],
      cta: "START NOW",
      badge: null
    },
    {
      name: "BUSINESS PRO",
      price: "€7,500",
      popular: true,
      features: [
        "🚀 Full-Stack Web Application",
        "🚀 Custom Admin Dashboard",
        "🚀 Database & API Integration",
        "🚀 Payment Gateway Setup",
        "🚀 6 Months Free Maintenance",
        "🚀 Priority Support & Training",
        "⚡ 4 Week Delivery"
      ],
      cta: "MOST POPULAR",
      badge: "BEST VALUE"
    },
    {
      name: "ENTERPRISE SUITE",
      price: "€15,000+",
      popular: false,
      features: [
        "💎 Advanced Custom Solutions",
        "💎 AI Integration & Automation", 
        "💎 Multi-Platform Development",
        "💎 Dedicated Development Team",
        "💎 1 Year Free Maintenance",
        "💎 24/7 Premium Support",
        "⚡ Custom Timeline"
      ],
      cta: "CONTACT US",
      badge: null
    }
  ];

  return (
    <section id="pricing" className="pricing-section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Investment Plans</h2>
          <p className="section-subtitle">Choose the perfect package for your digital transformation</p>
          <div className="pricing-guarantee">
            💰 <strong>MONEY-BACK GUARANTEE:</strong> If you're not 100% satisfied, we refund every penny!
          </div>
        </div>
        <div className="pricing-grid">
          {pricingPlans.map((plan, index) => (
            <div key={index} className={`pricing-card ${plan.popular ? 'popular' : ''}`}>
              {plan.badge && <div className="pricing-badge">{plan.badge}</div>}
              <div className="pricing-header">
                <h3 className="plan-name">{plan.name}</h3>
                <div className="plan-price">{plan.price}</div>
                <div className="plan-billing">One-time investment</div>
              </div>
              <ul className="pricing-features">
                {plan.features.map((feature, idx) => (
                  <li key={idx}>{feature}</li>
                ))}
              </ul>
              <button 
                className={`pricing-btn ${plan.popular ? 'popular-btn' : ''}`}
                onClick={() => {
                  const contactSection = document.getElementById('contact');
                  if (contactSection) {
                    contactSection.scrollIntoView({
                      behavior: 'smooth',
                      block: 'start'
                    });
                    // Focus on contact form after scroll
                    setTimeout(() => {
                      const nameInput = document.querySelector('input[name="name"]');
                      if (nameInput) {
                        nameInput.focus();
                      }
                    }, 1000);
                  }
                }}
              >
                {plan.cta}
              </button>
              {plan.popular && (
                <div className="popular-ribbon">
                  <span>RECOMMENDED</span>
                </div>
              )}
            </div>
          ))}
        </div>
        <div className="pricing-footer">
          <div className="intellectual-property-notice">
            <h4>🛡️ Intellectual Property Policy</h4>
            <p><strong>Code Ownership:</strong> All source code, frameworks, and proprietary solutions developed by 019solutions remain our intellectual property.</p>
            <p><strong>Client License:</strong> Clients receive usage rights for their specific project implementation with clearly defined terms.</p>
            <p><strong>Protection Guarantee:</strong> Your project includes our proven, tested, and legally protected codebase ensuring long-term reliability.</p>
          </div>
          <p><strong>FREE CONSULTATION:</strong> Not sure which package? Let's discuss your project!</p>
          <p><strong>URGENT PROJECTS:</strong> Need it faster? Premium rush delivery available!</p>
        </div>
      </div>
    </section>
  );
};
// Testimonials Section
const Testimonials = () => {
  const [testimonials, setTestimonials] = useState([]);

  useEffect(() => {
    const fetchTestimonials = async () => {
      try {
        const response = await axios.get(`${API}/testimonials`);
        setTestimonials(response.data);
      } catch (error) {
        console.error('Error fetching testimonials:', error);
      }
    };
    fetchTestimonials();
  }, []);

  return (
    <section className="testimonials-section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">What Our Clients Say</h2>
          <p className="section-subtitle">Real feedback from satisfied clients</p>
        </div>
        <div className="testimonials-grid">
          {testimonials.map((testimonial, index) => (
            <div key={testimonial.id} className="testimonial-card" style={{animationDelay: `${index * 0.2}s`}}>
              <div className="testimonial-rating">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <span key={i} className="star">⭐</span>
                ))}
              </div>
              <p className="testimonial-content">"{testimonial.content}"</p>
              <div className="testimonial-author">
                <img src={testimonial.avatar} alt={testimonial.name} className="author-avatar" />
                <div className="author-info">
                  <div className="author-name">{testimonial.name}</div>
                  <div className="author-role">{testimonial.role} at {testimonial.company}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Freelancers Marketplace Section
const FreelancersMarketplace = () => {
  const [freelancers, setFreelancers] = useState([]);

  useEffect(() => {
    const fetchFreelancers = async () => {
      try {
        const response = await axios.get(`${API}/freelancers`);
        setFreelancers(response.data);
      } catch (error) {
        console.error('Error fetching freelancers:', error);
      }
    };
    fetchFreelancers();
  }, []);

  return (
    <section id="freelancers" className="freelancers-section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Featured Freelancers</h2>
          <p className="section-subtitle">Connect with top talent in our network</p>
        </div>
        <div className="freelancers-grid">
          {freelancers.map((freelancer, index) => (
            <div key={freelancer.id} className="freelancer-card" style={{animationDelay: `${index * 0.2}s`}}>
              <div className="freelancer-header">
                <img src={freelancer.avatar} alt={freelancer.name} className="freelancer-avatar" />
                <div className="freelancer-info">
                  <h3 className="freelancer-name">{freelancer.name}</h3>
                  <div className="freelancer-title">{freelancer.title}</div>
                  <div className="freelancer-rate">{freelancer.hourly_rate}</div>
                </div>
              </div>
              <p className="freelancer-bio">{freelancer.bio}</p>
              <div className="freelancer-skills">
                {freelancer.skills.map((skill, idx) => (
                  <span key={idx} className="skill-tag">{skill}</span>
                ))}
              </div>
              <div className="freelancer-availability">
                Status: <span className="availability-status">{freelancer.availability}</span>
              </div>
              <button className="freelancer-contact-btn">Contact</button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Contact Section
const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    subject: '',
    message: '',
    service_interest: '',
    budget_range: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await axios.post(`${API}/contact`, formData);
      setSubmitMessage('Thank you! Your message has been sent successfully.');
      setFormData({
        name: '',
        email: '',
        company: '',
        subject: '',
        message: '',
        service_interest: '',
        budget_range: ''
      });
    } catch (error) {
      setSubmitMessage('Sorry, there was an error sending your message. Please try again.');
    }
    setIsSubmitting(false);
  };

  return (
    <section id="contact" className="contact-section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Let's Work Together</h2>
          <p className="section-subtitle">Ready to bring your vision to life?</p>
        </div>
        <div className="contact-content">
          <div className="contact-info">
            <div className="contact-item">
              <div className="contact-icon">EMAIL</div>
              <div>
                <h4>Business Email</h4>
                <p><a href="mailto:contact@019solutions.com">contact@019solutions.com</a></p>
              </div>
            </div>
            <div className="contact-item">
              <div className="contact-icon">PHONE</div>
              <div>
                <h4>Business Phone</h4>
                <p><a href="tel:+41787664181">+41 78 766 41 81</a></p>
              </div>
            </div>
            <div className="contact-item">
              <div className="contact-icon">CHAT</div>
              <div>
                <h4>WhatsApp & Viber</h4>
                <p>
                  <a href="https://wa.me/41787664181" target="_blank" rel="noopener noreferrer">WhatsApp</a> • 
                  <a href="viber://chat?number=41787664181" target="_blank" rel="noopener noreferrer">Viber</a>
                </p>
              </div>
            </div>
          </div>
          
          <form className="contact-form" onSubmit={handleSubmit}>
            <div className="form-row">
              <input
                type="text"
                name="name"
                placeholder="Your Name *"
                value={formData.name}
                onChange={handleChange}
                required
                className="form-input"
              />
              <input
                type="email"
                name="email"
                placeholder="Email Address *"
                value={formData.email}
                onChange={handleChange}
                required
                className="form-input"
              />
            </div>
            <div className="form-row">
              <input
                type="text"
                name="company"
                placeholder="Company Name"
                value={formData.company}
                onChange={handleChange}
                className="form-input"
              />
              <select
                name="service_interest"
                value={formData.service_interest}
                onChange={handleChange}
                className="form-input"
              >
                <option value="">Service of Interest</option>
                <option value="full-stack">Full-Stack Development</option>
                <option value="responsive">Responsive Design</option>
                <option value="ecommerce">E-commerce Solutions</option>
                <option value="performance">Performance Optimization</option>
                <option value="gaming">Gaming Solutions</option>
                <option value="ai">AI Integration</option>
                <option value="consulting">Consulting</option>
              </select>
            </div>
            <input
              type="text"
              name="subject"
              placeholder="Project Subject *"
              value={formData.subject}
              onChange={handleChange}
              required
              className="form-input"
            />
            <textarea
              name="message"
              placeholder="Tell us about your project *"
              value={formData.message}
              onChange={handleChange}
              required
              className="form-textarea"
              rows="5"
            ></textarea>
            <select
              name="budget_range"
              value={formData.budget_range}
              onChange={handleChange}
              className="form-input"
            >
              <option value="">Budget Range</option>
              <option value="under-5k">Under $5,000</option>
              <option value="5k-15k">$5,000 - $15,000</option>
              <option value="15k-50k">$15,000 - $50,000</option>
              <option value="50k-plus">$50,000+</option>
            </select>
            
            <button 
              type="submit" 
              disabled={isSubmitting}
              className="submit-btn"
            >
              {isSubmitting ? 'Sending...' : 'Send Message'}
            </button>
            
            {submitMessage && (
              <div className={`submit-message ${submitMessage.includes('error') ? 'error' : 'success'}`}>
                {submitMessage}
              </div>
            )}
          </form>
        </div>
      </div>
    </section>
  );
};

// Footer
const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="footer-logo"></div>
            <h3>019 SOLUTIONS</h3>
            <p>Transforming ideas into digital reality</p>
          </div>
          
          <div className="footer-links">
            <div className="footer-column">
              <h4>Services</h4>
              <ul>
                <li><a href="#services">Web Development</a></li>
                <li><a href="#services">Gaming Solutions</a></li>
                <li><a href="#services">E-commerce</a></li>
                <li><a href="#services">Consulting</a></li>
              </ul>
            </div>
            
            <div className="footer-column">
              <h4>Company</h4>
              <ul>
                <li><a href="#portfolio">Portfolio</a></li>
                <li><a href="#freelancers">Freelancers</a></li>
                <li><a href="#contact">Contact</a></li>
                <li><a href="#pricing">Pricing</a></li>
              </ul>
            </div>
            
            <div className="footer-column">
              <h4>Legal</h4>
              <ul>
                <li><a href="#contact">IP Policy</a></li>
                <li><a href="#contact">Terms of Service</a></li>
                <li><a href="#contact">Privacy Policy</a></li>
                <li><a href="#contact">Licensing</a></li>
              </ul>
            </div>
            
            <div className="footer-column">
              <h4>Connect</h4>
              <ul>
                <li><a href="mailto:contact@019solutions.com">Business Email</a></li>
                <li><a href="mailto:risticvladica@hotmail.com">Direct Contact</a></li>
                <li><a href="tel:+41787664181">Phone: +41 78 766 41 81</a></li>
                <li><a href="https://wa.me/41787664181" target="_blank" rel="noopener noreferrer">WhatsApp</a></li>
                <li><a href="viber://chat?number=41787664181" target="_blank" rel="noopener noreferrer">Viber</a></li>
              </ul>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <div className="business-info">
            <p><strong>019 Solutions</strong> - Professional Digital Development Company</p>
            <p><a href="mailto:contact@019solutions.com">contact@019solutions.com</a> • <a href="tel:+41787664181">+41 78 766 41 81</a></p>
            <p><a href="https://wa.me/41787664181" target="_blank" rel="noopener noreferrer">WhatsApp</a> • <a href="viber://chat?number=41787664181" target="_blank" rel="noopener noreferrer">Viber</a> • <a href="mailto:risticvladica@hotmail.com">risticvladica@hotmail.com</a></p>
            <p><strong>www.019solutions.com</strong> • Switzerland</p>
          </div>
          <p>&copy; 2025 019 Solutions. All rights reserved.</p>
          <div className="legal-notice">
            <small>All source code, designs, and intellectual property developed by 019solutions remain proprietary assets of the company. Licensed usage terms apply to all delivered projects.</small>
          </div>
        </div>
      </div>
    </footer>
  );
};

// Main App Component
function App() {
  return (
    <div className="App">
      <MatrixBackground />
      <Hero />
      <Services />
      <Portfolio />
      <Pricing />
      <Testimonials />
      <FreelancersMarketplace />
      <Contact />
      <Footer />
    </div>
  );
}

export default App;