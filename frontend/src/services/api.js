import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth endpoints
export const auth = {
  register: (username, twitterUsername) =>
    api.post('/auth/register', null, { params: { username, twitter_username: twitterUsername } }),
  login: (username, password) =>
    api.post('/auth/login', { username, password }),
};

// Tweet endpoints
export const tweets = {
  getAll: (status, limit = 50) =>
    api.get('/api/tweets/', { params: { status, limit } }),
  getOne: (id) => api.get(`/api/tweets/${id}`),
  create: (data) => api.post('/api/tweets/', data),
  post: (id) => api.post(`/api/tweets/${id}/post`),
};

// AI endpoints
export const ai = {
  generate: (data) => api.post('/api/ai/generate', data),
  analyze: (text) => api.post('/api/ai/analyze', null, { params: { text } }),
};

// Analytics endpoints
export const analytics = {
  getSummary: (days = 30) =>
    api.get('/api/analytics/summary', { params: { days } }),
  getTweetMetrics: (tweetId) =>
    api.get(`/api/analytics/tweets/${tweetId}/metrics`),
  getEngagementTrends: (days = 30) =>
    api.get('/api/analytics/engagement-trends', { params: { days } }),
};

// Campaign endpoints
export const campaigns = {
  getAll: () => api.get('/api/campaigns/'),
  getOne: (id) => api.get(`/api/campaigns/${id}`),
  create: (data) => api.post('/api/campaigns/', data),
  update: (id, data) => api.put(`/api/campaigns/${id}`, data),
  delete: (id) => api.delete(`/api/campaigns/${id}`),
  toggle: (id) => api.post(`/api/campaigns/${id}/toggle`),
};

export default api;
