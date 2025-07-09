import axios, {
  type AxiosError,
  type InternalAxiosRequestConfig,
} from "axios";
import { API_BASE_URL, ENDPOINTS } from "../config/api";

// Create axios instance with default config
// Create axios instance with default config
console.log('API Base URL:', API_BASE_URL); // Debug log

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Required for cookies and authentication
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
    "X-Requested-With": "XMLHttpRequest",
  },
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
  timeout: 10000, // Reduced timeout to 10 seconds for faster feedback
});

// Add response interceptor for better error logging
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', {
      message: error.message,
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
    });
    return Promise.reject(error);
  }
);

// Cache for CSRF token
let csrfTokenCache: string | null = null;

// Request interceptor to add CSRF token to requests
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Skip CSRF token for token refresh request to avoid infinite loops
    if (config.url?.includes(ENDPOINTS.AUTH.CSRF)) {
      return config;
    }

    // Only add CSRF token for state-changing requests
    if (
      ["POST", "PUT", "PATCH", "DELETE"].includes(
        (config.method || "").toUpperCase()
      )
    ) {
      try {
        // Use cached token if available
        if (!csrfTokenCache) {
          csrfTokenCache = await getCSRFToken();
        }

        if (csrfTokenCache) {
          config.headers.set("X-CSRFToken", csrfTokenCache, true);
        }
      } catch (error) {
        console.warn("Failed to get CSRF token:", error);
        // Continue with the request - the server will validate the token
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 403 Forbidden (CSRF token issues)
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    // If error is 403 and we haven't tried to refresh the token yet
    if (error.response?.status === 403 && !originalRequest._retry) {
      // Clear the cached token to force a refresh
      csrfTokenCache = null;

      try {
        // Try to get a new CSRF token
        const newToken = await getCSRFToken();
        if (newToken) {
          // Update the authorization header
          originalRequest.headers["X-CSRFToken"] = newToken;
          // Retry the original request
          return api(originalRequest);
        }
      } catch (error) {
        console.error("Failed to refresh CSRF token:", error);
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
            Accept: "application/json",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            Pragma: "no-cache",
            Expires: "0",
          },
        }
      );

      if (response.data?.csrfToken) {
        csrfToken = response.data.csrfToken;
        return csrfToken;
      }

      throw new Error("No CSRF token received in response");
    } catch (error) {
      console.error("Error fetching CSRF token:", error);
      // Clear the promise so we can retry
      csrfPromise = null;
      throw new Error("Failed to retrieve CSRF token");
    }
  })();

  return csrfPromise;
}

// Export api instance with proper typing
export default api;
