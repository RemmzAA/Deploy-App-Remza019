import React from 'react';

const PaymentMethodSelector = ({ selectedMethod, onMethodSelect }) => {
  const paymentMethods = [
    {
      id: 'paypal',
      name: 'PayPal',
      icon: '💳',
      description: 'Pay with your PayPal account'
    },
    {
      id: 'card',
      name: 'Credit Card',
      icon: '💳',
      description: 'Visa, Mastercard, American Express'
    }
  ];

  return (
    <div className="method-selection">
      {paymentMethods.map((method) => (
        <div 
          key={method.id}
          className={`payment-option ${selectedMethod === method.id ? 'selected' : ''}`}
          onClick={() => onMethodSelect(method.id)}
        >
          <div className="payment-icon">{method.icon}</div>
          <h3>{method.name}</h3>
          <p>{method.description}</p>
        </div>
      ))}
    </div>
  );
};

export default PaymentMethodSelector;