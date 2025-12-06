import React, { useState, useEffect } from 'react';
import './LicenseGenerator.css';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const LicenseGenerator = () => {
  const [licenses, setLicenses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [licenseType, setLicenseType] = useState('PREMIUM');
  const [duration, setDuration] = useState(7);
  const [generatedKey, setGeneratedKey] = useState('');
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadLicenses();
    loadStats();
  }, []);

  const loadLicenses = async () => {
    try {
      const response = await fetch(`${API_URL}/api/license/list`);
      const data = await response.json();
      if (data.success) {
        setLicenses(data.licenses);
      }
    } catch (error) {
      console.error('Failed to load licenses:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/license/stats`);
      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const generateLicense = async () => {
    setLoading(true);
    setGeneratedKey('');

    try {
      const response = await fetch(`${API_URL}/api/license/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          license_type: licenseType,
          duration_days: licenseType === 'TRIAL' ? duration : null
        })
      });

      const data = await response.json();

      if (data.success) {
        setGeneratedKey(data.license_key);
        await loadLicenses();
        await loadStats();
        alert(`✅ License kreiran uspešno!\n\nKey: ${data.license_key}\nTip: ${data.license_type}`);
      } else {
        alert(`❌ Greška: ${data.message || 'Nepoznata greška'}`);
      }
    } catch (error) {
      alert(`❌ Greška pri generisanju: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('✅ Kopirano u clipboard!');
  };

  const deleteLicense = async (licenseKey) => {
    if (!window.confirm(`Da li ste sigurni da želite da obrišete:\n${licenseKey}?`)) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/license/delete/${licenseKey}`, {
        method: 'DELETE'
      });
      const data = await response.json();

      if (data.success) {
        alert('✅ License obrisan!');
        await loadLicenses();
        await loadStats();
      } else {
        alert(`❌ Greška: ${data.message}`);
      }
    } catch (error) {
      alert(`❌ Greška: ${error.message}`);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('sr-Latn-RS');
  };

  return (
    <div className="license-generator">
      <h2>🔑 License Generator</h2>

      {/* Stats */}
      {stats && (
        <div className="license-stats">
          <div className="stat-card">
            <span className="stat-value">{stats.total}</span>
            <span className="stat-label">Ukupno</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{stats.active}</span>
            <span className="stat-label">Aktivni</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{stats.premium}</span>
            <span className="stat-label">Premium</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{stats.trial}</span>
            <span className="stat-label">Trial</span>
          </div>
        </div>
      )}

      {/* Generator Form */}
      <div className="generator-form">
        <h3>Kreiraj Novi License</h3>
        
        <div className="form-group">
          <label>Tip License:</label>
          <select value={licenseType} onChange={(e) => setLicenseType(e.target.value)}>
            <option value="PREMIUM">PREMIUM (Zauvek)</option>
            <option value="TRIAL">TRIAL (Ograničeno)</option>
            <option value="BASIC">BASIC</option>
          </select>
        </div>

        {licenseType === 'TRIAL' && (
          <div className="form-group">
            <label>Trajanje (dana):</label>
            <input
              type="number"
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value))}
              min="1"
              max="365"
            />
          </div>
        )}

        <button
          className="generate-btn"
          onClick={generateLicense}
          disabled={loading}
        >
          {loading ? '⏳ Generisanje...' : '🔑 Generiši License'}
        </button>

        {generatedKey && (
          <div className="generated-key">
            <h4>✅ Novi License Key:</h4>
            <div className="key-display">
              <code>{generatedKey}</code>
              <button onClick={() => copyToClipboard(generatedKey)}>📋 Kopiraj</button>
            </div>
          </div>
        )}
      </div>

      {/* License List */}
      <div className="license-list">
        <h3>Svi License Keys ({licenses.length})</h3>
        <div className="license-table">
          <table>
            <thead>
              <tr>
                <th>License Key</th>
                <th>Tip</th>
                <th>Status</th>
                <th>Kreiran</th>
                <th>Aktiviran</th>
                <th>Ističe</th>
                <th>Akcije</th>
              </tr>
            </thead>
            <tbody>
              {licenses.map((license) => (
                <tr key={license.license_key || license._id}>
                  <td>
                    <code className="license-key-cell">{license.license_key}</code>
                    <button
                      className="copy-btn-small"
                      onClick={() => copyToClipboard(license.license_key)}
                    >
                      📋
                    </button>
                  </td>
                  <td>
                    <span className={`badge badge-${license.license_type?.toLowerCase()}`}>
                      {license.license_type || 'N/A'}
                    </span>
                  </td>
                  <td>
                    <span className={`status ${license.is_active ? 'active' : 'inactive'}`}>
                      {license.is_active ? '✅ Aktivan' : '❌ Neaktivan'}
                    </span>
                  </td>
                  <td>{formatDate(license.created_at)}</td>
                  <td>{formatDate(license.activated_at)}</td>
                  <td>{formatDate(license.expires_at) || '♾️ Nikada'}</td>
                  <td>
                    <button
                      className="delete-btn"
                      onClick={() => deleteLicense(license.license_key)}
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default LicenseGenerator;
