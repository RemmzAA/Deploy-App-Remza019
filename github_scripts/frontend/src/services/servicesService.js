import axios from 'axios';

const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const servicesService = {
  async fetchServices() {
    try {
      const response = await axios.get(`${API_BASE}/services`, {
        timeout: 10000, // 10 second timeout
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Services service error:', error);
      
      if (error.response) {
        throw new Error(`Server error: ${error.response.status} - ${error.response.data?.message || 'Failed to fetch services'}`);
      } else if (error.request) {
        throw new Error('Network error: Unable to reach server');
      } else {
        throw new Error(`Request error: ${error.message}`);
      }
    }
  },

  async getServiceById(serviceId) {
    try {
      const response = await axios.get(`${API_BASE}/services/${serviceId}`, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Services service error:', error);
      throw this.handleError(error);
    }
  },

  handleError(error) {
    if (error.response) {
      return new Error(`Server error: ${error.response.status} - ${error.response.data?.message || 'Unknown error'}`);
    } else if (error.request) {
      return new Error('Network error: Unable to reach server');
    } else {
      return new Error(`Request error: ${error.message}`);
    }
  }
};