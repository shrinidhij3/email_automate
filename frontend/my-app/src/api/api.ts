import axios, { AxiosError } from 'axios';
import { API_BASE_URL } from '../config/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // Important: This enables sending cookies with cross-origin requests
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

// Request interceptor to add CSRF token to requests
api.interceptors.request.use(
  async (config) => {
    // Only add CSRF token for non-GET requests
    if (config.method?.toUpperCase() !== 'GET') {
      const csrfToken = await getCSRFToken();
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 403 Forbidden (CSRF token issues)
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    
    // If error is 403 and we haven't tried to refresh the token yet
    if (error.response?.status === 403 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to get a new CSRF token
        const newToken = await getCSRFToken();
        if (newToken) {
          // Update the authorization header
          originalRequest.headers['X-CSRFToken'] = newToken;
          // Retry the original request
          return api(originalRequest);
        }
      } catch (error) {
        console.error('Failed to refresh CSRF token:', error);
      }
    }
    
    return Promise.reject(error);
  }
);

// Function to get CSRF token
let csrfToken: string | null = null;

export async function getCSRFToken(): Promise<string> {
  // Return cached token if available
  if (csrfToken) return csrfToken;
  
  try {
    const response = await axios.get<{ csrfToken: string }>(`${API_BASE_URL}/api/csrf-token/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });

    if (response.data?.csrfToken) {
      const token = response.data.csrfToken;
      csrfToken = token;
      return token;
    }
    
    throw new Error('No CSRF token received');
  } catch (error) {
    console.error('Error fetching CSRF token:', error);
    throw error;
  }
}

// Export api instance with proper typing
export default api;
