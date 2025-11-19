import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './MerchStore.css';

const MerchStore = ({ user }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cart, setCart] = useState([]);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    setLoading(true);
    
    // Demo products (would fetch from API in production)
    const demoProducts = [
      {
        id: 'merch_001',
        name: 'REMZA019 Gaming T-Shirt',
        description: 'Premium quality Matrix-themed gaming t-shirt',
        price: 29.99,
        currency: 'USD',
        image_url: 'https://via.placeholder.com/400x400/000000/00ff00?text=T-SHIRT',
        stock: 50,
        category: 'apparel'
      },
      {
        id: 'merch_002',
        name: 'Gaming Hoodie',
        description: 'Comfortable hoodie with REMZA019 logo',
        price: 49.99,
        currency: 'USD',
        image_url: 'https://via.placeholder.com/400x400/000000/00ff00?text=HOODIE',
        stock: 30,
        category: 'apparel'
      },
      {
        id: 'merch_003',
        name: 'Gaming Mousepad',
        description: 'Large RGB mousepad with Matrix design',
        price: 19.99,
        currency: 'USD',
        image_url: 'https://via.placeholder.com/400x400/000000/00ff00?text=MOUSEPAD',
        stock: 100,
        category: 'accessories'
      },
      {
        id: 'merch_004',
        name: 'REMZA019 Cap',
        description: 'Adjustable gaming cap with embroidered logo',
        price: 24.99,
        currency: 'USD',
        image_url: 'https://via.placeholder.com/400x400/000000/00ff00?text=CAP',
        stock: 75,
        category: 'apparel'
      },
      {
        id: 'merch_005',
        name: 'Gaming Sticker Pack',
        description: 'Set of 10 premium vinyl stickers',
        price: 9.99,
        currency: 'USD',
        image_url: 'https://via.placeholder.com/400x400/000000/00ff00?text=STICKERS',
        stock: 200,
        category: 'accessories'
      },
      {
        id: 'merch_006',
        name: 'Fortnite Mug',
        description: 'Ceramic mug with Fortnite themed design',
        price: 14.99,
        currency: 'USD',
        image_url: 'https://via.placeholder.com/400x400/000000/00ff00?text=MUG',
        stock: 60,
        category: 'accessories'
      }
    ];

    setProducts(demoProducts);
    setLoading(false);
  };

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    
    if (existingItem) {
      setCart(cart.map(item =>
        item.id === product.id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  const updateQuantity = (productId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }

    setCart(cart.map(item =>
      item.id === productId ? { ...item, quantity } : item
    ));
  };

  const getTotalPrice = () => {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0).toFixed(2);
  };

  return (
    <div className="merch-store-container">
      <motion.div
        className="merch-store-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2>🛍️ Official Merch Store</h2>
        <p>Support REMZA019 Gaming with exclusive merchandise</p>
      </motion.div>

      {cart.length > 0 && (
        <motion.div
          className="cart-summary"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="cart-header">
            <h3>🛒 Cart ({cart.length} items)</h3>
            <button className="clear-cart" onClick={() => setCart([])}>
              Clear Cart
            </button>
          </div>

          <div className="cart-items">
            {cart.map(item => (
              <div key={item.id} className="cart-item">
                <img src={item.image_url} alt={item.name} />
                <div className="cart-item-info">
                  <h4>{item.name}</h4>
                  <p>${item.price.toFixed(2)}</p>
                </div>
                <div className="quantity-controls">
                  <button onClick={() => updateQuantity(item.id, item.quantity - 1)}>-</button>
                  <span>{item.quantity}</span>
                  <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>+</button>
                </div>
                <button className="remove-item" onClick={() => removeFromCart(item.id)}>
                  🗑️
                </button>
              </div>
            ))}
          </div>

          <div className="cart-total">
            <h3>Total: ${getTotalPrice()}</h3>
            <button className="checkout-btn" onClick={() => alert('Checkout coming soon!')}>
              💳 Checkout
            </button>
          </div>
        </motion.div>
      )}

      <div className="products-grid">
        {loading ? (
          <div className="loading">Loading products...</div>
        ) : (
          products.map((product, index) => (
            <motion.div
              key={product.id}
              className="product-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className="product-image">
                <img src={product.image_url} alt={product.name} />
                {product.stock < 10 && (
                  <span className="low-stock-badge">Only {product.stock} left!</span>
                )}
              </div>

              <div className="product-info">
                <h3>{product.name}</h3>
                <p className="product-description">{product.description}</p>

                <div className="product-footer">
                  <span className="product-price">${product.price.toFixed(2)}</span>
                  <button
                    className="add-to-cart-btn"
                    onClick={() => addToCart(product)}
                    disabled={product.stock === 0}
                  >
                    {product.stock === 0 ? '❌ Out of Stock' : '🛒 Add to Cart'}
                  </button>
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export default MerchStore;
