export const notificationService = {
  playVoiceNotification(message) {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(message);
      utterance.lang = 'en-US';
      utterance.volume = 0.5;
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      
      // Optional: Set specific voice
      const voices = speechSynthesis.getVoices();
      if (voices.length > 0) {
        // Try to find a female voice first
        const femaleVoice = voices.find(voice => 
          voice.name.toLowerCase().includes('female') ||
          voice.name.toLowerCase().includes('karen') ||
          voice.name.toLowerCase().includes('samantha')
        );
        
        if (femaleVoice) {
          utterance.voice = femaleVoice;
        }
      }
      
      speechSynthesis.speak(utterance);
    }
  },

  requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  },

  showBrowserNotification(title, body, icon = null) {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body,
        icon: icon || '/favicon.ico',
        badge: '/favicon.ico',
        timestamp: Date.now(),
        requireInteraction: false
      });
    }
  },

  formatNotificationTime(timestamp) {
    const now = new Date();
    const diff = now - timestamp;
    
    if (diff < 60000) { // Less than 1 minute
      return 'Just now';
    } else if (diff < 3600000) { // Less than 1 hour
      const minutes = Math.floor(diff / 60000);
      return `${minutes} min ago`;
    } else if (diff < 86400000) { // Less than 24 hours
      const hours = Math.floor(diff / 3600000);
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
      return timestamp.toLocaleDateString();
    }
  }
};