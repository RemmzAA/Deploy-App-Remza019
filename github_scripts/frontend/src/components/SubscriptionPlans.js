import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SubscriptionPlans.css';

const SubscriptionPlans = ({ user, onSubscribe }) => {
  const [plans, setPlans] = useState({});
  const [loading, setLoading] = useState(true);
  const [currentSubscription, setCurrentSubscription] = useState(null);

  useEffect(() => {
    fetchPlans();
    if (user) {
      fetchCurrentSubscription();
    }
  }, [user]);

  const fetchPlans = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/subscriptions/plans`);
      setPlans(response.data.plans);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching plans:', error);
      setLoading(false);
    }
  };

  const fetchCurrentSubscription = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/subscriptions/user/${user.id}`);
      if (response.data.has_subscription) {
        setCurrentSubscription(response.data);
      }
    } catch (error) {
      console.error('Error fetching subscription:', error);
    }
  };

  const handleSubscribe = async (planKey) => {
    if (!user) {
      alert('Please login first!');
      return;
    }

    try {
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/subscriptions/create`, {
        user_id: user.id,
        plan: planKey,
        email: user.email
      });

      if (response.data.success) {
        alert(`✅ ${response.data.message}`);
        if (onSubscribe) onSubscribe(response.data);
      }
    } catch (error) {
      console.error('Error subscribing:', error);
      alert('Failed to create subscription. Please try again.');
    }
  };

  if (loading) {
    return <div className="subscription-loading">Loading plans...</div>;
  }

  return (
    <div className="subscription-plans-container">
      <div className="plans-header">
        <h2>💎 Premium Membership Plans</h2>
        <p>Support the channel and get exclusive perks!</p>
      </div>

      {currentSubscription && (
        <div className="current-subscription-banner">
          <h3>✅ Active Subscription: {currentSubscription.plan_name}</h3>
          <p>Expires: {new Date(currentSubscription.current_period_end).toLocaleDateString()}</p>
        </div>
      )}

      <div className="plans-grid">
        {Object.entries(plans).map(([key, plan]) => (
          <div 
            key={key} 
            className={`plan-card ${key === 'pro' ? 'featured' : ''} ${currentSubscription?.plan === key ? 'active' : ''}`}
          >
            {key === 'pro' && <div className="featured-badge">MOST POPULAR</div>}
            
            <div className="plan-header">
              <h3>{plan.name}</h3>
              <div className="plan-price">
                <span className="price">${plan.price}</span>
                <span className="interval">/month</span>
              </div>
            </div>

            <div className="plan-features">
              {plan.features.map((feature, index) => (
                <div key={index} className="feature-item">
                  <span className="check-icon">✓</span>
                  <span>{feature}</span>
                </div>
              ))}
            </div>

            <button 
              className={`subscribe-btn ${currentSubscription?.plan === key ? 'active' : ''}`}
              onClick={() => handleSubscribe(key)}
              disabled={currentSubscription?.plan === key}
            >
              {currentSubscription?.plan === key ? 'Current Plan' : `Subscribe to ${plan.name}`}
            </button>

            {key === 'vip' && (
              <div className="vip-badge">
                <span>🌟 VIP EXCLUSIVE 🌟</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SubscriptionPlans;
