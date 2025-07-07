import axios from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios';

// Determine environment
const isProduction = import.meta.env.PROD || import.meta.env.VITE_ENV === 'production';
const API_BASE_URL = isProduction 
  ? 'https://email-automate-ob1a.onrender.com' 
  : 'http://localhost:8000';

console.log(`API Base URL: ${API_BASE_URL}`);

// Create axios instance with default config
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  withXSRFToken: true,
});

// Track if we're currently refreshing the CSRF token
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: unknown) => void;
  reject: (reason?: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Function to get CSRF token from cookies
const getCsrfToken = (): string | null => {
  if (typeof document === 'undefined') return null;
  const cookieValue = document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrftoken='))
    ?.split('=')[1];
  return cookieValue ? decodeURIComponent(cookieValue) : null;
};

// Function to fetch a new CSRF token
const fetchCsrfToken = async (): Promise<string | null> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/csrf-token/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
      },
    });
    
    if (response.data?.csrfToken) {
      const token = response.data.csrfToken;
      // Update the cookie for future requests
      document.cookie = `csrftoken=${token}; Path=/; SameSite=Lax${!import.meta.env.DEV ? '; Secure' : ''}`;
      return token;
    }
    return null;
  } catch (error) {
    console.error('Error fetching CSRF token:', error);
    return null;
  }
};

// Request interceptor to add CSRF token to requests
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Skip CSRF token for certain endpoints
    const skipCSRF = [
      '/api/auth/csrf-token/',
      '/api/auth/login/',
      '/api/auth/register/',
    ].some(path => config.url?.includes(path));

    if (skipCSRF || config.method?.toLowerCase() === 'get') {
      return config;
    }

    // Get CSRF token from cookie
    let csrfToken = getCsrfToken();
    
    // If no CSRF token in cookies, fetch a new one
    if (!csrfToken) {
      csrfToken = await fetchCsrfToken();
    }

    // Add CSRF token to headers if available
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    // Update CSRF token from response headers if available
    const csrfToken = response.headers['x-csrftoken'] || response.headers['X-CSRFToken'];
    if (csrfToken) {
      document.cookie = `csrftoken=${csrfToken}; Path=/; SameSite=Lax${!import.meta.env.DEV ? '; Secure' : ''}`;
    }
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    
    // If there's no response, it's a network error
    if (!error.response) {
      console.error('Network Error:', error);
      return Promise.reject(error);
    }

    // Handle 403 Forbidden errors (might be CSRF related)
    if (error.response.status === 403 && !originalRequest?._retry) {
      // If we're already refreshing the token, add the request to the queue
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers['X-CSRFToken'] = token;
            }
            return api(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Try to get a new CSRF token
        const newCsrfToken = await fetchCsrfToken();
        
        if (newCsrfToken) {
          // Process the queue with the new token
          processQueue(null, newCsrfToken);
          
          // Update the original request with new CSRF token
          if (originalRequest.headers) {
            originalRequest.headers['X-CSRFToken'] = newCsrfToken;
          }
          
          // Retry the original request
          return api(originalRequest);
        } else {
          throw new Error('Failed to refresh CSRF token');
        }
      } catch (csrfError) {
        console.error('Error refreshing CSRF token:', csrfError);
        processQueue(csrfError, null);
        
        // If we can't get a new CSRF token, redirect to login
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        
        return Promise.reject(csrfError);
      } finally {
        isRefreshing = false;
      }
    } else if (error.response.status === 401) {
      // Handle unauthorized (401) errors
      console.error('Authentication failed:', error);
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
