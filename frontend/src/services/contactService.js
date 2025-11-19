import axios from 'axios';

const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const contactService = {
  async submitContact(contactData) {
    try {
      const response = await axios.post(`${API_BASE}/contact`, contactData, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 10000, // 10 second timeout
      });
      
      return response.data;
    } catch (error) {
      console.error('Contact service error:', error);
      
      if (error.response) {
        // Server responded with error status
        throw new Error(`Server error: ${error.response.status} - ${error.response.data?.message || 'Unknown error'}`);
      } else if (error.request) {
        // Network error
        throw new Error('Network error: Unable to reach server');
      } else {
        // Other error
        throw new Error(`Request error: ${error.message}`);
      }
    }
  }
};