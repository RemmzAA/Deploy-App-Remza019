import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import './AdminSchedulePanel.css';

const AdminSchedulePanel = () => {
  const { token } = useAuth();
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState(null);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  
  const [formData, setFormData] = useState({
    day: 'Monday',
    time: '20:00',
    game: '',
    description: '',
    duration: '2-3 hours',
    active: true
  });

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  // Load schedules
  const loadSchedules = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/schedule/list`);
      const data = await response.json();
      
      if (data.success) {
        setSchedules(data.schedules || []);
      }
      setLoading(false);
    } catch (error) {
      console.error('Failed to load schedules:', error);
      showMessage('Failed to load schedules', 'error');
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSchedules();
  }, []);

  const showMessage = (text, type = 'success') => {
    setMessage(text);
    setMessageType(type);
    setTimeout(() => {
      setMessage('');
      setMessageType('');
    }, 3000);
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.game.trim()) {
      showMessage('Please enter a game name', 'error');
      return;
    }

    try {
      const url = editingSchedule
        ? `${process.env.REACT_APP_BACKEND_URL}/api/schedule/update/${editingSchedule.id}`
        : `${process.env.REACT_APP_BACKEND_URL}/api/schedule/add`;
      
      const method = editingSchedule ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (data.success) {
        showMessage(
          editingSchedule ? 'Schedule updated successfully!' : 'Schedule added successfully!',
          'success'
        );
        loadSchedules();
        resetForm();
      } else {
        showMessage(data.message || 'Operation failed', 'error');
      }
    } catch (error) {
      console.error('Save schedule error:', error);
      showMessage('Network error. Please try again.', 'error');
    }
  };

  const handleEdit = (schedule) => {
    setEditingSchedule(schedule);
    setFormData({
      day: schedule.day,
      time: schedule.time,
      game: schedule.game,
      description: schedule.description || '',
      duration: schedule.duration || '2-3 hours',
      active: schedule.active
    });
    setShowForm(true);
  };

  const handleDelete = async (scheduleId) => {
    if (!window.confirm('Are you sure you want to delete this schedule?')) {
      return;
    }

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/schedule/delete/${scheduleId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      const data = await response.json();

      if (data.success) {
        showMessage('Schedule deleted successfully!', 'success');
        loadSchedules();
      } else {
        showMessage(data.message || 'Delete failed', 'error');
      }
    } catch (error) {
      console.error('Delete schedule error:', error);
      showMessage('Network error. Please try again.', 'error');
    }
  };

  const resetForm = () => {
    setFormData({
      day: 'Monday',
      time: '20:00',
      game: '',
      description: '',
      duration: '2-3 hours',
      active: true
    });
    setEditingSchedule(null);
    setShowForm(false);
  };

  if (loading) {
    return <div className="admin-schedule-panel loading">Loading schedules...</div>;
  }

  return (
    <div className="admin-schedule-panel">
      <div className="panel-header">
        <h2>📅 Stream Schedule Management</h2>
        <motion.button
          className="add-schedule-btn"
          onClick={() => setShowForm(!showForm)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {showForm ? '❌ Cancel' : '➕ Add Schedule'}
        </motion.button>
      </div>

      {/* Message Display */}
      <AnimatePresence>
        {message && (
          <motion.div
            className={`message ${messageType}`}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {message}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Schedule Form */}
      <AnimatePresence>
        {showForm && (
          <motion.form
            className="schedule-form"
            onSubmit={handleSubmit}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <h3>{editingSchedule ? '✏️ Edit Schedule' : '➕ Add New Schedule'}</h3>
            
            <div className="form-grid">
              <div className="form-group">
                <label>Day</label>
                <select name="day" value={formData.day} onChange={handleInputChange}>
                  {days.map(day => (
                    <option key={day} value={day}>{day}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Time</label>
                <input
                  type="time"
                  name="time"
                  value={formData.time}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Game *</label>
                <input
                  type="text"
                  name="game"
                  value={formData.game}
                  onChange={handleInputChange}
                  placeholder="e.g., CS2, Valorant"
                  required
                />
              </div>

              <div className="form-group">
                <label>Duration</label>
                <input
                  type="text"
                  name="duration"
                  value={formData.duration}
                  onChange={handleInputChange}
                  placeholder="e.g., 2-3 hours"
                />
              </div>
            </div>

            <div className="form-group full-width">
              <label>Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Optional description"
                rows="3"
              />
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="active"
                  checked={formData.active}
                  onChange={handleInputChange}
                />
                Active (visible to users)
              </label>
            </div>

            <div className="form-actions">
              <button type="submit" className="save-btn">
                {editingSchedule ? '💾 Update' : '➕ Add'} Schedule
              </button>
              <button type="button" className="cancel-btn" onClick={resetForm}>
                ❌ Cancel
              </button>
            </div>
          </motion.form>
        )}
      </AnimatePresence>

      {/* Schedules List */}
      <div className="schedules-list">
        <h3>Current Schedules ({schedules.length})</h3>
        {schedules.length === 0 ? (
          <p className="no-schedules">No schedules yet. Add your first one!</p>
        ) : (
          <div className="schedules-grid">
            {schedules.map((schedule) => (
              <motion.div
                key={schedule.id}
                className={`schedule-card ${!schedule.active ? 'inactive' : ''}`}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                whileHover={{ scale: 1.02 }}
              >
                <div className="schedule-header">
                  <div className="day-time">
                    <span className="day">{schedule.day}</span>
                    <span className="time">🕐 {schedule.time}</span>
                  </div>
                  {!schedule.active && <span className="inactive-badge">Inactive</span>}
                </div>
                
                <h4 className="game">🎮 {schedule.game}</h4>
                {schedule.description && (
                  <p className="description">{schedule.description}</p>
                )}
                <p className="duration">⏱️ {schedule.duration}</p>

                <div className="schedule-actions">
                  <button
                    className="edit-btn"
                    onClick={() => handleEdit(schedule)}
                  >
                    ✏️ Edit
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => handleDelete(schedule.id)}
                  >
                    🗑️ Delete
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminSchedulePanel;
