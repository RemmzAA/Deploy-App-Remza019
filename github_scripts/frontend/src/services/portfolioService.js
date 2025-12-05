import axios from 'axios';

const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const portfolioService = {
  async fetchProjects() {
    try {
      const response = await axios.get(`${API_BASE}/projects`, {
        timeout: 10000, // 10 second timeout
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Portfolio service error:', error);
      
      if (error.response) {
        throw new Error(`Server error: ${error.response.status} - ${error.response.data?.message || 'Failed to fetch projects'}`);
      } else if (error.request) {
        throw new Error('Network error: Unable to reach server');
      } else {
        throw new Error(`Request error: ${error.message}`);
      }
    }
  },

  async getProjectById(projectId) {
    try {
      const response = await axios.get(`${API_BASE}/projects/${projectId}`, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Portfolio service error:', error);
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