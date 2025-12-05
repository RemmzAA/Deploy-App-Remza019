import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import './AdminDashboard.css';

const AdminDashboard = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState('content');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  
  // Content State - SIMPLIFIED
  const [aboutLines, setAboutLines] = useState([]);
  const [tags, setTags] = useState([]);
  
  // Load data on mount
  useEffect(() => {
    loadContentData();
  }, []);

  const loadContentData = async () => {
    try {
      setLoading(true);
      
      // Load about content
      const aboutRes = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/admin/content`);
      if (aboutRes.data.content) {
        setAboutLines(aboutRes.data.content.map(line => ({ id: uuidv4(), text: line })));
      }
      
      // Load tags
      const tagsRes = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/admin/content/tags`);
      if (tagsRes.data.tags) {
        setTags(tagsRes.data.tags.map(tag => ({ ...tag, id: uuidv4() })));
      }
      
      setLoading(false);
      showMessage('✅ Content loaded successfully!', 'success');
    } catch (error) {
      console.error('Error loading content:', error);
      showMessage('❌ Failed to load content', 'error');
      setLoading(false);
    }
  };

  const showMessage = (msg, type = 'info') => {
    setMessage(msg);
    setTimeout(() => setMessage(''), 3000);
  };

  // ABOUT LINES MANAGEMENT
  const addAboutLine = () => {
    setAboutLines([...aboutLines, { id: uuidv4(), text: '' }]);
  };

  const updateAboutLine = (id, value) => {
    setAboutLines(aboutLines.map(line => 
      line.id === id ? { ...line, text: value } : line
    ));
  };

  const removeAboutLine = (id) => {
    setAboutLines(aboutLines.filter(line => line.id !== id));
  };

  const saveAboutContent = async () => {
    try {
      setLoading(true);
      const content = aboutLines.map(line => line.text).filter(text => text.trim());
      
      await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/admin/content`, { content });
      
      showMessage('✅ About content saved!', 'success');
      setLoading(false);
    } catch (error) {
      console.error('Error saving about content:', error);
      showMessage('❌ Failed to save content', 'error');
      setLoading(false);
    }
  };

  // TAGS MANAGEMENT
  const addTag = () => {
    setTags([...tags, { id: uuidv4(), icon: '🎮', text: '' }]);
  };

  const updateTag = (id, field, value) => {
    setTags(tags.map(tag => 
      tag.id === id ? { ...tag, [field]: value } : tag
    ));
  };

  const removeTag = (id) => {
    setTags(tags.filter(tag => tag.id !== id));
  };

  const saveTags = async () => {
    try {
      setLoading(true);
      const tagsToSave = tags
        .filter(tag => tag.icon && tag.text.trim())
        .map(({ icon, text }) => ({ icon, text }));
      
      await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/admin/content/tags`, { tags: tagsToSave });
      
      showMessage('✅ Tags saved successfully!', 'success');
      setLoading(false);
    } catch (error) {
      console.error('Error saving tags:', error);
      showMessage('❌ Failed to save tags', 'error');
      setLoading(false);
    }
  };

  return (
    <div className="admin-dashboard-overlay">
      <div className="admin-dashboard-modal">
        {/* Header */}
        <div className="admin-dashboard-header">
          <h2>⚙️ Admin Dashboard</h2>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>

        {/* Message Banner */}
        {message && (
          <div className={`admin-message ${message.includes('✅') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}

        {/* Tabs */}
        <div className="admin-tabs">
          <button 
            className={activeTab === 'content' ? 'active' : ''}
            onClick={() => setActiveTab('content')}
          >
            📝 Content
          </button>
          <button 
            className={activeTab === 'live' ? 'active' : ''}
            onClick={() => setActiveTab('live')}
          >
            🔴 Live
          </button>
          <button 
            className={activeTab === 'stats' ? 'active' : ''}
            onClick={() => setActiveTab('stats')}
          >
            📊 Stats
          </button>
        </div>

        {/* Tab Content */}
        <div className="admin-tab-content">
          {activeTab === 'content' && (
            <div className="content-tab">
              <h3>About Section</h3>
              
              {/* About Lines Editor */}
              <div className="about-editor">
                {aboutLines.map((line) => (
                  <div key={line.id} className="input-row">
                    <input
                      type="text"
                      value={line.text}
                      onChange={(e) => updateAboutLine(line.id, e.target.value)}
                      placeholder="Enter about text..."
                      className="admin-input"
                    />
                    <button onClick={() => removeAboutLine(line.id)} className="remove-btn">
                      🗑️
                    </button>
                  </div>
                ))}
                <button onClick={addAboutLine} className="add-btn">
                  ➕ Add Line
                </button>
                <button onClick={saveAboutContent} className="save-btn" disabled={loading}>
                  {loading ? '⏳ Saving...' : '💾 Save About'}
                </button>
              </div>

              <hr className="divider" />

              <h3>Tags</h3>
              
              {/* Tags Editor */}
              <div className="tags-editor">
                {tags.map((tag) => (
                  <div key={tag.id} className="input-row tag-row">
                    <input
                      type="text"
                      value={tag.icon}
                      onChange={(e) => updateTag(tag.id, 'icon', e.target.value)}
                      placeholder="🎮"
                      className="admin-input icon-input"
                      maxLength={2}
                    />
                    <input
                      type="text"
                      value={tag.text}
                      onChange={(e) => updateTag(tag.id, 'text', e.target.value)}
                      placeholder="Tag text..."
                      className="admin-input tag-text-input"
                    />
                    <button onClick={() => removeTag(tag.id)} className="remove-btn">
                      🗑️
                    </button>
                  </div>
                ))}
                <button onClick={addTag} className="add-btn">
                  ➕ Add Tag
                </button>
                <button onClick={saveTags} className="save-btn" disabled={loading}>
                  {loading ? '⏳ Saving...' : '💾 Save Tags'}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'live' && (
            <div className="live-tab">
              <h3>🔴 Live Stream Management</h3>
              <p>Coming soon: Live stream controls</p>
            </div>
          )}

          {activeTab === 'stats' && (
            <div className="stats-tab">
              <h3>📊 Statistics</h3>
              <p>Coming soon: Analytics dashboard</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
