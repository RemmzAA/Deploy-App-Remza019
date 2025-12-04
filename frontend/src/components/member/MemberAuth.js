import React, { useState } from 'react';
import './MemberAuth.css';

const MemberAuth = ({ onAuthSuccess }) => {
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [formData, setFormData] = useState({
    nickname: '',
    discord_id: '',
    email: '',
    verification_code: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [step, setStep] = useState(1); // 1: input form, 2: verify code

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/member/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nickname: formData.nickname,
          discord_id: formData.discord_id,
          email: formData.email
        })
      });

      const data = await response.json();

      if (data.success) {
        setSuccess('Registration successful! Check your email for verification code.');
        // Show verification code if email failed
        if (data.verification_code) {
          setSuccess(`Registration successful! Your verification code is: ${data.verification_code}`);
        }
        setStep(2);
      } else {
        setError(data.detail || 'Registration failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/member/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          verification_code: step === 2 ? formData.verification_code : null
        })
      });

      const data = await response.json();

      if (data.success) {
        if (data.token) {
          // Login successful
          localStorage.setItem('member_token', data.token);
          localStorage.setItem('member_data', JSON.stringify(data.member));
          setSuccess('Login successful!');
          if (onAuthSuccess) {
            onAuthSuccess(data.member, data.token);
          }
        } else if (data.requires_verification) {
          // Show verification code if email failed, otherwise show sent message
          if (data.verification_code) {
            setSuccess(`Verification code: ${data.verification_code}`);
          } else {
            setSuccess('Verification code sent to your email!');
          }
          setStep(2);
        }
      } else {
        if (data.detail && data.detail.includes('pending')) {
          setError('⏳ Your account is pending admin verification. Please wait for approval.');
        } else {
          setError(data.detail || 'Login failed');
        }
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyEmail = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/member/verify-email?email=${formData.email}&code=${formData.verification_code}`,
        { method: 'POST' }
      );

      const data = await response.json();

      if (data.success && data.token) {
        localStorage.setItem('member_token', data.token);
        localStorage.setItem('member_data', JSON.stringify(data.member));
        setSuccess('Email verified! Redirecting...');
        
        setTimeout(() => {
          if (onAuthSuccess) {
            onAuthSuccess(data.member, data.token);
          }
        }, 1000);
      } else {
        setError(data.detail || 'Verification failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="member-auth-container">
      <div className="member-auth-box">
        <h2 className="auth-title">
          {mode === 'register' ? '🎮 Member Registration' : '🔐 Member Login'}
        </h2>

        {error && <div className="auth-message error">{error}</div>}
        {success && <div className="auth-message success">{success}</div>}

        {step === 1 ? (
          <form onSubmit={mode === 'register' ? handleRegister : handleLogin} className="auth-form">
            {mode === 'register' && (
              <>
                <div className="form-group">
                  <label>Nickname</label>
                  <input
                    type="text"
                    name="nickname"
                    value={formData.nickname}
                    onChange={handleChange}
                    placeholder="Enter your nickname"
                    required
                    minLength={3}
                    maxLength={30}
                  />
                </div>

                <div className="form-group">
                  <label>Discord ID</label>
                  <input
                    type="text"
                    name="discord_id"
                    value={formData.discord_id}
                    onChange={handleChange}
                    placeholder="e.g., remza019#1234"
                    required
                  />
                </div>
              </>
            )}

            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your@email.com"
                required
              />
            </div>

            <button type="submit" className="auth-button" disabled={loading}>
              {loading ? '⏳ Processing...' : mode === 'register' ? '✅ Register' : '🚀 Login'}
            </button>
          </form>
        ) : (
          <form onSubmit={mode === 'register' ? handleVerifyEmail : handleLogin} className="auth-form">
            <div className="form-group">
              <label>Verification Code</label>
              <input
                type="text"
                name="verification_code"
                value={formData.verification_code}
                onChange={handleChange}
                placeholder="Enter 6-digit code"
                required
                maxLength={6}
              />
            </div>

            <button type="submit" className="auth-button" disabled={loading}>
              {loading ? '⏳ Verifying...' : '✅ Verify'}
            </button>

            <button
              type="button"
              className="auth-link-button"
              onClick={() => setStep(1)}
            >
              ← Back
            </button>
          </form>
        )}

        <div className="auth-switch">
          {mode === 'register' ? (
            <p>
              Already have an account?{' '}
              <button
                type="button"
                className="auth-link-button"
                onClick={() => {
                  setMode('login');
                  setStep(1);
                  setError('');
                  setSuccess('');
                }}
              >
                Login here
              </button>
            </p>
          ) : (
            <p>
              Don't have an account?{' '}
              <button
                type="button"
                className="auth-link-button"
                onClick={() => {
                  setMode('register');
                  setStep(1);
                  setError('');
                  setSuccess('');
                }}
              >
                Register here
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default MemberAuth;
