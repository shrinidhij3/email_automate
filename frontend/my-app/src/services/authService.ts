import axios from "axios";
import { API_BASE_URL, ENDPOINTS } from "../config/api";
import { fetchCSRFToken } from "../utils/csrf"; // Import the dedicated CSRF function

export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthResponse extends User {}

export interface ErrorResponse {
  error?: string;
  [key: string]: any;
}

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // Required for cookies to be sent cross-domain
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
  xsrfCookieName: 'csrftoken',
  // Django expects the CSRF token in the HTTP_X_CSRFTOKEN header
  xsrfHeaderName: 'X-CSRFToken',  // This will be transformed to HTTP_X_CSRFTOKEN by Django
  // Important for cross-domain requests
  withXSRFToken: true,
  timeout: 10000,  // 10 second timeout
});

// Add a request interceptor to transform the header name if needed
api.interceptors.request.use(config => {
  // If there's a CSRF token in the headers, make sure it's using the correct header name
  if (config.headers && config.headers['X-CSRFToken']) {
    config.headers['HTTP_X_CSRFTOKEN'] = config.headers['X-CSRFToken'];
    delete config.headers['X-CSRFToken'];
  }
  return config;
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, {
      data: config.data,
      headers: config.headers,
      withCredentials: config.withCredentials,
    });
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for handling errors
api.interceptors.response.use(
  (response) => {
    console.log(`[API] Response ${response.status} ${response.config.url}`, {
      data: response.data,
      headers: response.headers,
    });
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // If 403 and not a retry, try to refresh CSRF token
    if (error.response?.status === 403 && !originalRequest._retry) {
      originalRequest._retry = true;
      console.log('CSRF token may be invalid, attempting to refresh...');
      
      try {
        await fetchCSRFToken();
        // Retry the original request with new CSRF token
        return api(originalRequest);
      } catch (refreshError) {
        console.error('Failed to refresh CSRF token:', refreshError);
        // Redirect to login on refresh failure
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Add response interceptor to handle CSRF token refresh
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    // If error is 403 and we haven't tried to refresh the token yet
    if (error.response?.status === 403 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to get a new CSRF token
        await fetchCSRFToken();
        // Retry the original request with the new token
        return api(originalRequest);
      } catch (refreshError) {
        console.error('Failed to refresh CSRF token:', refreshError);
        // If refresh fails, redirect to login
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Function to get CSRF token from cookies (keep as fallback)
export function getCSRFToken(): string | null {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : null;
}

const authService = {
  async register(
    username: string,
    email: string,
    password: string,
    password2: string,
    firstName: string = "",
    lastName: string = ""
  ): Promise<AuthResponse> {
    // Validate required fields
    if (!username || !email || !password || !password2) {
      throw new Error("All fields are required");
    }

    if (password !== password2) {
      throw new Error("Passwords do not match");
    }

    try {
      // Get a fresh CSRF token before registration
      const csrfToken = await fetchCSRFToken();
      console.log('CSRF token for registration:', csrfToken);

      const registrationData = {
        username: username.trim(),
        email: email.trim(),
        password: password,
        password2: password2,
        first_name: firstName.trim(),
        last_name: lastName.trim(),
      };

      console.log('Registration data:', { ...registrationData, password: '***' });

      const response = await api.post<AuthResponse>(
        ENDPOINTS.AUTH.REGISTER,
        registrationData,
        {
          headers: {
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
          validateStatus: (status) => status < 500,
        }
      );

      console.log('Registration response:', {
        status: response.status,
        headers: response.headers,
        data: response.data
      });

      if (response.status === 201 || response.status === 200) {
        console.log("Registration successful, attempting auto-login...");

        // After successful registration, try to log the user in
        try {
          console.log('Initiating auto-login after registration');
          const loginResponse = await this.login(username, password);
          console.log('Auto-login successful:', loginResponse);
          return loginResponse;
        } catch (loginError) {
          console.warn("Auto-login after registration failed:", loginError);
          // Even if auto-login fails, return the registration response
          return response.data;
        }
      } else {
        console.error('Registration failed with status:', response.status, response.data);
        const errorMessage = (response.data as any)?.detail || 
                          (response.data as any)?.error || 
                          `Registration failed with status: ${response.status}`;
        throw new Error(errorMessage);
      }
    } catch (error: unknown) {
      console.error("Registration error:", error);

      if (axios.isAxiosError(error) && error.response) {
        const responseData = error.response.data as any;

        if (error.response.status === 400) {
          const fieldErrors: string[] = [];

          if (responseData && typeof responseData === "object") {
            for (const [field, messages] of Object.entries(responseData)) {
              if (Array.isArray(messages)) {
                fieldErrors.push(`${field}: ${(messages as string[])[0]}`);
              } else if (typeof messages === "string") {
                fieldErrors.push(`${field}: ${messages}`);
              }
            }

            if (fieldErrors.length > 0) {
              throw new Error(`Validation error: ${fieldErrors.join(", ")}`);
            }
          }

          if (responseData?.error) {
            throw new Error(String(responseData.error));
          }

          throw new Error("Registration failed. Please check your input.");
        }

        throw new Error(
          `Registration failed with status: ${error.response.status}`
        );
      }

      if (error instanceof Error) {
        throw error;
      }

      throw new Error("An unknown error occurred during registration.");
    }
  },

  async login(username: string, password: string): Promise<AuthResponse> {
    try {
      // First get a fresh CSRF token
      const csrfToken = await fetchCSRFToken();
      
      // Then make the login request with the token
      const response = await api.post(
        ENDPOINTS.AUTH.LOGIN,
        { username, password },
        {
          headers: {
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
          validateStatus: (status) => status < 500,
        }
      );

      console.log('Login response:', {
        status: response.status,
        data: response.data,
        headers: response.headers
      });

      if (response.status === 200) {
        // Verify we have a session cookie
        const hasSession = document.cookie.includes('sessionid');
        console.log('Login successful. Session cookie present:', hasSession);
        
        // Return the user data from the response
        return response.data.user || response.data;
      } else {
        const errorMessage = response.data?.message || 'Login failed';
        throw new Error(errorMessage);
      }
    } catch (error: any) {
      console.error("Login error:", {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
      });

      if (axios.isAxiosError(error) && error.response) {
        const errorData = error.response.data as ErrorResponse;
        const message = errorData?.error || "Login failed";
        throw new Error(message);
      }

      throw new Error("Network error during login");
    }
  },

  async logout(): Promise<void> {
    try {
      const csrfToken = await fetchCSRFToken();

      const response = await api.post(
        ENDPOINTS.AUTH.LOGOUT,
        {},
        {
          headers: {
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
          validateStatus: (status) => status < 500,
        }
      );

      console.log('Logout response:', {
        status: response.status,
        data: response.data,
        headers: response.headers
      });

      if (response.status !== 200) {
        const errorMessage = response.data?.message || 'Logout failed';
        throw new Error(errorMessage);
      }
      
      // Clear any stored user data
      localStorage.removeItem('user');
      
    } catch (error) {
      console.error("Logout error:", error);
      // Even if there's an error, we want to clear the user's session
      localStorage.removeItem('user');
      throw error;
    }
  },

  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await api.get(ENDPOINTS.AUTH.USER, {
        withCredentials: true,
        validateStatus: (status) => status < 500,
      });

      console.log('Current user response:', {
        status: response.status,
        data: response.data,
        headers: response.headers
      });

      if (response.status === 200) {
        // Return the user data from the response
        return response.data.user || response.data;
      }
      
      // If we get here, the user is not authenticated
      return null;
    } catch (error) {
      console.error("Error fetching current user:", error);
      return null;
    }
  },

  async isAuthenticated(): Promise<boolean> {
    try {
      const user = await this.getCurrentUser();
      return user !== null;
    } catch (error) {
      console.error("Authentication check failed:", error);
      return false;
    }
  },
};

export default authService;
