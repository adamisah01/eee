import { state } from './state.js';

const BASE_URL = 'http://localhost:8001/api'; // Fallback for real API url later

export const API = {
  request: async (endpoint, options = {}) => {
    const url = `${BASE_URL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (state.token) {
      headers['Authorization'] = `Bearer ${state.token}`;
    }

    const config = {
      ...options,
      headers
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        if (response.status === 401) {
          state.setUser(null, null);
          window.location.hash = '#/login';
        }
        throw new Error(data.message || 'Something went wrong');
      }

      return data;
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  },

  get: (endpoint) => API.request(endpoint, { method: 'GET' }),
  post: (endpoint, body) => API.request(endpoint, { method: 'POST', body: JSON.stringify(body) }),
  put: (endpoint, body) => API.request(endpoint, { method: 'PUT', body: JSON.stringify(body) }),
  delete: (endpoint) => API.request(endpoint, { method: 'DELETE' })
};
