import React, { useState, useEffect } from 'react';
import './AdminFeaturesPanel.css';

const AdminFeaturesPanel = () => {
  const [features, setFeatures] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingFeature, setEditingFeature] = useState(null);
  const [formData, setFormData] = useState({
    icon: '',
    title: '',
    description: '',
    tooltip: '',
    enabled: true
  });

  // Load features on mount
  useEffect(() => {
    fetchFeatures();
  }, []);

  const fetchFeatures = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/features`);
      const data = await response.json();
      setFeatures(data);
      console.log('✅ Admin features loaded:', data.length);
    } catch (error) {
      console.error('❌ Failed to load features:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const url = editingFeature
        ? `${process.env.REACT_APP_BACKEND_URL}/api/admin/features/${editingFeature.id}`
        : `${process.env.REACT_APP_BACKEND_URL}/api/admin/features`;
      
      const method = editingFeature ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        console.log(`✅ Feature ${editingFeature ? 'updated' : 'created'}`);
        await fetchFeatures();
        resetForm();
      } else {
        console.error('❌ Failed to save feature');
      }
    } catch (error) {
      console.error('❌ Error saving feature:', error);
    }
  };

  const handleDelete = async (featureId) => {
    if (!window.confirm('Da li ste sigurni da želite da obrišete ovu feature karticu?')) {
      return;
    }
    
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/features/${featureId}`,
        { method: 'DELETE' }
      );
      
      if (response.ok) {
        console.log('✅ Feature deleted');
        await fetchFeatures();
      } else {
        console.error('❌ Failed to delete feature');
      }
    } catch (error) {
      console.error('❌ Error deleting feature:', error);
    }
  };

  const handleToggleEnabled = async (feature) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/features/${feature.id}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ enabled: !feature.enabled })
        }
      );
      
      if (response.ok) {
        console.log('✅ Feature enabled status toggled');
        await fetchFeatures();
      }
    } catch (error) {
      console.error('❌ Error toggling feature:', error);
    }
  };

  const startEdit = (feature) => {
    setEditingFeature(feature);
    setFormData({
      icon: feature.icon,
      title: feature.title,
      description: feature.description,
      tooltip: feature.tooltip,
      enabled: feature.enabled
    });
    setShowAddModal(true);
  };

  const resetForm = () => {
    setFormData({
      icon: '',
      title: '',
      description: '',
      tooltip: '',
      enabled: true
    });
    setEditingFeature(null);
    setShowAddModal(false);
  };

  return (
    <div className="admin-features-panel">
      <div className="panel-header">
        <h2>🎯 Features Management</h2>
        <button 
          className="add-feature-btn"
          onClick={() => setShowAddModal(true)}
        >
          ➕ Add New Feature
        </button>
      </div>

      <div className="features-list">
        {features.map((feature, index) => (
          <div key={feature.id} className={`feature-item ${!feature.enabled ? 'disabled' : ''}`}>
            <div className="feature-order">#{index + 1}</div>
            <div className="feature-icon-display">{feature.icon}</div>
            <div className="feature-details">
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
              <small className="tooltip-preview">💡 {feature.tooltip}</small>
            </div>
            <div className="feature-actions">
              <button
                className={`toggle-btn ${feature.enabled ? 'enabled' : 'disabled'}`}
                onClick={() => handleToggleEnabled(feature)}
                title={feature.enabled ? 'Disable' : 'Enable'}
              >
                {feature.enabled ? '👁️' : '🚫'}
              </button>
              <button
                className="edit-btn"
                onClick={() => startEdit(feature)}
                title="Edit"
              >
                ✏️
              </button>
              <button
                className="delete-btn"
                onClick={() => handleDelete(feature.id)}
                title="Delete"
              >
                🗑️
              </button>
            </div>
          </div>
        ))}
      </div>

      {showAddModal && (
        <div className="modal-overlay" onClick={resetForm}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingFeature ? 'Edit Feature' : 'Add New Feature'}</h3>
              <button className="close-btn" onClick={resetForm}>✖️</button>
            </div>
            
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Icon (Emoji):</label>
                <input
                  type="text"
                  value={formData.icon}
                  onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                  placeholder="📺"
                  required
                  maxLength={10}
                />
              </div>

              <div className="form-group">
                <label>Title:</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="GLEDAJ I ZARAĐUJ"
                  required
                />
              </div>

              <div className="form-group">
                <label>Description:</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Zarađuj poene gledanjem strimova"
                  required
                  rows={2}
                />
              </div>

              <div className="form-group">
                <label>Tooltip (Hover Text):</label>
                <textarea
                  value={formData.tooltip}
                  onChange={(e) => setFormData({ ...formData, tooltip: e.target.value })}
                  placeholder="Earn 5 points for every 10 minutes..."
                  required
                  rows={3}
                />
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.enabled}
                    onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                  />
                  Enabled
                </label>
              </div>

              <div className="modal-actions">
                <button type="button" className="cancel-btn" onClick={resetForm}>
                  Cancel
                </button>
                <button type="submit" className="save-btn">
                  {editingFeature ? 'Update' : 'Create'} Feature
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminFeaturesPanel;
