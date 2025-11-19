import axios from 'axios';

const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const paymentService = {
  async processPayPalPayment(amount) {
    try {
      const response = await axios.post(`${API_BASE}/payment/paypal`, {
        amount: parseFloat(amount),
        currency: 'EUR'
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 15000, // 15 second timeout for payments
      });
      
      return response.data;
    } catch (error) {
      console.error('PayPal payment error:', error);
      throw this.handlePaymentError(error);
    }
  },

  async processCardPayment(amount, cardDetails) {
    try {
      const response = await axios.post(`${API_BASE}/payment/card`, {
        amount: parseFloat(amount),
        currency: 'EUR',
        card: {
          number: cardDetails.number.replace(/\s/g, ''), // Remove spaces
          expiry: cardDetails.expiry,
          cvv: cardDetails.cvv,
          name: cardDetails.name
        }
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 15000, // 15 second timeout for payments
      });
      
      return response.data;
    } catch (error) {
      console.error('Card payment error:', error);
      throw this.handlePaymentError(error);
    }
  },

  handlePaymentError(error) {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const message = error.response.data?.message || 'Unknown payment error';
      
      switch (status) {
        case 400:
          return new Error(`Invalid payment data: ${message}`);
        case 402:
          return new Error(`Payment declined: ${message}`);
        case 500:
          return new Error('Payment processing temporarily unavailable');
        default:
          return new Error(`Payment error: ${message}`);
      }
    } else if (error.request) {
      // Network error
      return new Error('Unable to connect to payment processor');
    } else {
      // Other error
      return new Error(`Payment error: ${error.message}`);
    }
  }
};