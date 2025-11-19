import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import PaymentMethodSelector from './PaymentMethodSelector';
import CreditCardForm from './CreditCardForm';
import { paymentService } from '../services/paymentService';

const PaymentSystem = () => {
  const { t } = useTranslation();
  const [paymentMethod, setPaymentMethod] = useState('');
  const [amount, setAmount] = useState('');
  const [cardDetails, setCardDetails] = useState({
    number: '',
    expiry: '',
    cvv: '',
    name: ''
  });
  const [isProcessing, setIsProcessing] = useState(false);

  const handlePayPalPayment = async () => {
    if (!amount || amount <= 0) {
      alert('Please enter a valid amount');
      return;
    }

    setIsProcessing(true);
    try {
      const result = await paymentService.processPayPalPayment(amount);
      alert('PayPal integration ready - Connect with your PayPal Business Account');
    } catch (error) {
      alert('Payment failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCardPayment = async () => {
    if (!amount || amount <= 0) {
      alert('Please enter a valid amount');
      return;
    }

    if (!cardDetails.number || !cardDetails.expiry || !cardDetails.cvv || !cardDetails.name) {
      alert('Please fill in all card details');
      return;
    }

    setIsProcessing(true);
    try {
      const result = await paymentService.processCardPayment(amount, cardDetails);
      alert('Credit Card processing ready - Connect with Stripe API');
    } catch (error) {
      alert('Payment failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCardDetailsChange = (field, value) => {
    setCardDetails(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <section id="payment" className="payment-section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Payment Gateway</h2>
          <p className="section-subtitle">Secure payment processing for your services</p>
        </div>

        <div className="payment-methods">
          <PaymentMethodSelector
            selectedMethod={paymentMethod}
            onMethodSelect={setPaymentMethod}
          />

          {paymentMethod === 'card' && (
            <CreditCardForm
              cardDetails={cardDetails}
              onCardDetailsChange={handleCardDetailsChange}
            />
          )}

          <div className="amount-selection">
            <input
              type="number"
              placeholder="Amount (EUR)"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="amount-input"
              min="1"
              step="0.01"
            />
          </div>

          <button 
            className={`payment-submit-btn ${isProcessing ? 'processing' : ''}`}
            onClick={paymentMethod === 'paypal' ? handlePayPalPayment : handleCardPayment}
            disabled={isProcessing || !paymentMethod || !amount}
          >
            {isProcessing ? 'Processing...' : 
             paymentMethod === 'paypal' ? 'Pay with PayPal' : 'Process Payment'}
          </button>
        </div>
      </div>
    </section>
  );
};

export default PaymentSystem;