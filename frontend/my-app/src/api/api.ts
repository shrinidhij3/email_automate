import axios, { AxiosError } from 'axios';
import { API_BASE_URL } from '../config/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // Required for cookies and authentication
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  // Ensure credentials are sent with all requests
  withXSRFToken: true,
});

// Request interceptor to add CSRF token to requests
api.interceptors.request.use(
  async (config) => {
    // Always get CSRF token for all requests that can modify state
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(config.method?.toUpperCase() || '')) {
      try {
        const csrfToken = await getCSRFToken();
        if (csrfToken) {
          config.headers['X-CSRFToken'] = csrfToken;
        }
      } catch (error) {
        console.warn('Failed to get CSRF token:', error);
        // Don't block the request if CSRF token fetch fails
        // The server will validate the token and return an error if needed
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
let csrfPromise: Promise<string> | null = null;

export async function getCSRFToken(): Promise<string> {
  // Return cached token if available
  if (csrfToken) return csrfToken;
  
  // If a request is already in progress, return that promise
  if (csrfPromise) return csrfPromise;

  csrfPromise = (async () => {
    try {
      const response = await axios.get<{ csrfToken: string }>(
        `${API_BASE_URL}/api/auth/csrf-token/`,
        {
          withCredentials: true,
          headers: {
            'Accept': 'application/json',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
          },
        }
      );

      if (response.data?.csrfToken) {
        csrfToken = response.data.csrfToken;
        return csrfToken;
      }
      
      throw new Error('No CSRF token received in response');
    } catch (error) {
      console.error('Error fetching CSRF token:', error);
      // Clear the promise so we can retry
      csrfPromise = null;
      throw new Error('Failed to retrieve CSRF token');
    }
  })();

  return csrfPromise;
}

// Export api instance with proper typing
export default api;
