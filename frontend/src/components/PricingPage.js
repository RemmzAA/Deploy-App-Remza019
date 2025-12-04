import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import './PricingPage.css';

const PricingPage = () => {
  const navigate = useNavigate();

  const pricingPlans = [
    {
      id: 'trial',
      name: 'TRIAL',
      icon: '🧪',
      price: 'FREE',
      duration: '7-30 days',
      description: 'Perfect for trying out the platform',
      features: [
        'Limited time access',
        'Basic streaming features',
        'Community chat access',
        'Points & level system',
        'Email support'
      ],
      limitations: [
        'No custom emotes',
        'Basic badge only',
        'No priority support'
      ],
      buttonText: 'Request Trial',
      buttonClass: 'trial-button',
      popular: false
    },
    {
      id: 'basic',
      name: 'BASIC',
      icon: '⚡',
      price: 'Contact',
      duration: 'Monthly/Yearly',
      description: 'For regular viewers and supporters',
      features: [
        'Unlimited access',
        'All basic features',
        'Custom badge',
        'Priority chat',
        'Exclusive polls access',
        'Email & chat support',
        'Watch party invites',
        'Monthly giveaway entries'
      ],
      limitations: [
        'Limited custom emotes',
        'No VIP events access'
      ],
      buttonText: 'Get Started',
      buttonClass: 'basic-button',
      popular: false
    },
    {
      id: 'premium',
      name: 'PREMIUM',
      icon: '👑',
      price: 'Contact',
      duration: 'Monthly/Yearly',
      description: 'Ultimate experience for true fans',
      features: [
        'Everything in BASIC',
        'Custom logo watermark',
        'Unlimited custom emotes',
        'VIP badge & profile border',
        'Access to VIP-only events',
        'Priority support (24/7)',
        'Early access to features',
        'Private Discord channel',
        'Monthly 1-on-1 sessions',
        'Exclusive merchandise discounts',
        'Name in credits roll'
      ],
      limitations: [],
      buttonText: 'Go Premium',
      buttonClass: 'premium-button',
      popular: true
    }
  ];

  const handleSelectPlan = (planId) => {
    // Check if user is logged in as member
    const memberToken = localStorage.getItem('member_token');
    
    if (!memberToken) {
      // Redirect to member registration
      navigate('/member/login');
    } else {
      // Redirect to member dashboard license tab
      navigate('/member/dashboard');
    }
  };

  return (
    <div className="pricing-page">
      <div className="pricing-hero">
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="pricing-title">🎮 Choose Your Plan</h1>
          <p className="pricing-subtitle">
            Unlock exclusive features and support the community
          </p>
        </motion.div>
      </div>

      <div className="pricing-container">
        {pricingPlans.map((plan, index) => (
          <motion.div
            key={plan.id}
            className={`pricing-card ${plan.popular ? 'popular' : ''}`}
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.15 }}
          >
            {plan.popular && (
              <div className="popular-badge">
                ⭐ MOST POPULAR
              </div>
            )}

            <div className="plan-header">
              <div className="plan-icon">{plan.icon}</div>
              <h2 className="plan-name">{plan.name}</h2>
              <div className="plan-price">{plan.price}</div>
              <div className="plan-duration">{plan.duration}</div>
              <p className="plan-description">{plan.description}</p>
            </div>

            <div className="plan-features">
              <h3>✅ What's Included:</h3>
              <ul className="features-list">
                {plan.features.map((feature, idx) => (
                  <li key={idx} className="feature-item">
                    <span className="check-icon">✔️</span>
                    {feature}
                  </li>
                ))}
              </ul>

              {plan.limitations.length > 0 && (
                <>
                  <h3 className="limitations-title">⚠️ Limitations:</h3>
                  <ul className="limitations-list">
                    {plan.limitations.map((limitation, idx) => (
                      <li key={idx} className="limitation-item">
                        <span className="cross-icon">❌</span>
                        {limitation}
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>

            <button
              className={`plan-button ${plan.buttonClass}`}
              onClick={() => handleSelectPlan(plan.id)}
            >
              {plan.buttonText}
            </button>
          </motion.div>
        ))}
      </div>

      <div className="pricing-footer">
        <motion.div
          className="footer-content"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <h3>💬 Need Help Choosing?</h3>
          <p>
            Contact us on <a href="https://discord.gg/remza019" target="_blank" rel="noopener noreferrer">Discord</a> or email us for personalized recommendations
          </p>
          
          <div className="faq-section">
            <h3>❓ Frequently Asked Questions</h3>
            <div className="faq-grid">
              <div className="faq-item">
                <h4>How do I activate my license?</h4>
                <p>Register as a member, then go to your dashboard and enter your license key in the License tab.</p>
              </div>
              <div className="faq-item">
                <h4>Can I upgrade my plan?</h4>
                <p>Yes! Contact us anytime to upgrade from TRIAL to BASIC or BASIC to PREMIUM.</p>
              </div>
              <div className="faq-item">
                <h4>What payment methods do you accept?</h4>
                <p>We accept all major payment methods. Contact us for details on available options.</p>
              </div>
              <div className="faq-item">
                <h4>Is there a refund policy?</h4>
                <p>Yes, we offer a 14-day money-back guarantee for all paid plans.</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default PricingPage;
