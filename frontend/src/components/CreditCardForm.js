import React from 'react';

const CreditCardForm = ({ cardDetails, onCardDetailsChange }) => {
  const handleInputChange = (field) => (e) => {
    onCardDetailsChange(field, e.target.value);
  };

  // Format card number with spaces
  const formatCardNumber = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    const matches = v.match(/\d{4,16}/g);
    const match = matches && matches[0] || '';
    const parts = [];
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4));
    }
    if (parts.length) {
      return parts.join(' ');
    } else {
      return v;
    }
  };

  // Format expiry date as MM/YY
  const formatExpiry = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    if (v.length >= 2) {
      return `${v.slice(0, 2)}/${v.slice(2, 4)}`;
    }
    return v;
  };

  return (
    <div className="card-form">
      <input
        type="text"
        placeholder="Card Number"
        value={formatCardNumber(cardDetails.number)}
        onChange={(e) => onCardDetailsChange('number', e.target.value.replace(/\s/g, ''))}
        className="payment-input"
        maxLength="19" // 16 digits + 3 spaces
      />
      
      <div className="form-row">
        <input
          type="text"
          placeholder="MM/YY"
          value={formatExpiry(cardDetails.expiry)}
          onChange={(e) => onCardDetailsChange('expiry', e.target.value.replace(/[^0-9]/g, ''))}
          className="payment-input"
          maxLength="5"
        />
        <input
          type="text"
          placeholder="CVV"
          value={cardDetails.cvv}
          onChange={handleInputChange('cvv')}
          className="payment-input"
          maxLength="4"
        />
      </div>
      
      <input
        type="text"
        placeholder="Cardholder Name"
        value={cardDetails.name}
        onChange={handleInputChange('name')}
        className="payment-input"
      />
    </div>
  );
};

export default CreditCardForm;