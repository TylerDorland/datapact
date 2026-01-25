import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
const DICTIONARY_API_URL = import.meta.env.VITE_DICTIONARY_API_URL || 'http://localhost:8002';
const NOTIFICATION_API_URL = import.meta.env.VITE_NOTIFICATION_API_URL || 'http://localhost:8003';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const dictionaryClient = axios.create({
  baseURL: DICTIONARY_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const notificationClient = axios.create({
  baseURL: NOTIFICATION_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth (if needed later)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      // Could redirect to login here if auth is implemented
    }
    return Promise.reject(error);
  }
);
