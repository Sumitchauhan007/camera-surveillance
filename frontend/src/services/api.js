import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Camera Controls
export const cameraAPI = {
  start: () => api.post('/camera/start'),
  stop: () => api.post('/camera/stop'),
  getStatus: () => api.get('/camera/status'),
  getFrame: () => api.get('/camera/frame'),
  takeSnapshot: () => api.post('/camera/snapshot'),
};

// Recording Controls
export const recordingAPI = {
  start: () => api.post('/recording/start'),
  stop: () => api.post('/recording/stop'),
};

// Student Management
export const studentsAPI = {
  getAll: () => api.get('/students'),
  getOne: (id) => api.get(`/students/${id}`),
  add: (data) => api.post('/students', data),
  delete: (id) => api.delete(`/students/${id}`),
};

// Detections
export const detectionsAPI = {
  getRecent: (limit = 50) => api.get(`/detections/recent?limit=${limit}`),
  getByStudent: (name) => api.get(`/detections/student/${encodeURIComponent(name)}`),
};

// Alerts
export const alertsAPI = {
  getAll: () => api.get('/alerts'),
  acknowledge: (id) => api.post(`/alerts/${id}/acknowledge`),
};

// Statistics & Reports
export const reportsAPI = {
  getStatistics: () => api.get('/statistics'),
  getDailyReport: (date) => api.get(`/reports/daily?date=${date}`),
  getIntruderReport: () => api.get('/reports/intruders'),
};

// System
export const systemAPI = {
  health: () => api.get('/health'),
  getConfig: () => api.get('/config'),
};

export default api;
