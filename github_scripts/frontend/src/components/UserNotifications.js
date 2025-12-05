import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import NotificationCard from './NotificationCard';
import WorkIndicator from './WorkIndicator';
import { notificationService } from '../services/notificationService';

const UserNotifications = () => {
  const { t } = useTranslation();
  const [notifications, setNotifications] = useState([]);
  const [hasNewWork, setHasNewWork] = useState(false);

  useEffect(() => {
    // Simulate real-time notifications
    const interval = setInterval(() => {
      const newNotification = {
        id: Date.now(),
        type: 'work',
        message: 'New project request available',
        timestamp: new Date(),
        read: false
      };
      
      setNotifications(prev => [newNotification, ...prev.slice(0, 4)]);
      setHasNewWork(true);
      
      // Voice notification
      notificationService.playVoiceNotification('New work notification received');
    }, 30000); // Every 30 seconds for demo

    return () => clearInterval(interval);
  }, []);

  const markAsRead = (id) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === id ? { ...notif, read: true } : notif
      )
    );
    setHasNewWork(false);
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notif => ({ ...notif, read: true }))
    );
    setHasNewWork(false);
  };

  const clearAllNotifications = () => {
    setNotifications([]);
    setHasNewWork(false);
  };

  return (
    <section className="user-notifications-section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Client Dashboard</h2>
          <p className="section-subtitle">Real-time work notifications and project updates</p>
        </div>
        
        <div className="notifications-container">
          <WorkIndicator hasNewWork={hasNewWork} />

          <div className="notifications-header">
            <h3>Notifications ({notifications.length})</h3>
            {notifications.length > 0 && (
              <div className="notification-actions">
                <button onClick={markAllAsRead} className="action-btn">
                  Mark All Read
                </button>
                <button onClick={clearAllNotifications} className="action-btn clear">
                  Clear All
                </button>
              </div>
            )}
          </div>

          <div className="notifications-list">
            {notifications.length === 0 ? (
              <div className="no-notifications">
                <p>No notifications yet</p>
                <small>You'll receive real-time updates here</small>
              </div>
            ) : (
              notifications.map(notification => (
                <NotificationCard
                  key={notification.id}
                  notification={notification}
                  onMarkAsRead={markAsRead}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default UserNotifications;