import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ScheduleWidget.css';

const ScheduleWidget = () => {
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load schedules from backend
  const loadSchedules = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/schedule`);
      const data = await response.json();
      
      if (data.success && data.schedule) {
        setSchedules(data.schedule);
      }
      setLoading(false);
    } catch (err) {
      console.error('Failed to load schedules:', err);
      setError('Failed to load stream schedule');
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSchedules();

    // Listen for real-time schedule updates via SSE
    const clientId = `schedule-widget-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const eventSource = new EventSource(`${process.env.REACT_APP_BACKEND_URL}/api/sse/${clientId}`);
    
    eventSource.addEventListener('schedule_update', (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📅 Schedule update received:', data);
        if (data.schedule) {
          setSchedules(data.schedule);
          console.log('✅ Schedule updated in ScheduleWidget:', data.schedule);
        }
      } catch (e) {
        console.error('Failed to parse schedule update:', e);
      }
    });

    return () => {
      eventSource.close();
    };
  }, []);

  if (loading) {
    return (
      <div className="schedule-widget loading">
        <div className="loading-spinner">⏳</div>
        <p>Loading schedule...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="schedule-widget error">
        <p>{error}</p>
      </div>
    );
  }

  if (schedules.length === 0) {
    return (
      <div className="schedule-widget empty">
        <p>📅 No streams scheduled yet. Check back soon!</p>
      </div>
    );
  }

  return (
    <motion.div 
      className="schedule-widget"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <motion.h3 
        className="schedule-title"
        initial={{ scale: 0.9 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        📅 Stream Schedule
      </motion.h3>
      
      <div className="schedule-list">
        <AnimatePresence>
          {schedules.map((schedule, index) => (
            <motion.div
              key={schedule.id}
              className="schedule-item"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              whileHover={{ scale: 1.02, x: 5 }}
            >
              <div className="schedule-day">
                <span className="day-label">{schedule.day}</span>
                <span className="time-label">🕐 {schedule.time}</span>
              </div>
              
              <div className="schedule-details">
                <h4 className="game-name">🎮 {schedule.game}</h4>
                {schedule.description && (
                  <p className="schedule-description">{schedule.description}</p>
                )}
                <span className="schedule-duration">⏱️ {schedule.duration}</span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default ScheduleWidget;
