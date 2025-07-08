import axios from "axios";
import { API_BASE_URL, ENDPOINTS } from "../config/api";
import { fetchCSRFToken } from "../utils/csrf";

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

// Request cache to prevent duplicate API calls
const requestCache = new Map<string, Promise<any>>();

// Helper function to create cache key
function createCacheKey(method: string, url: string, data?: any): string {
  return `${method}:${url}:${JSON.stringify(data || {})}`;
}

// Helper function to cache requests
function cacheRequest<T>(key: string, requestPromise: Promise<T>): Promise<T> {
  requestCache.set(key, requestPromise);

  // Clean up cache when request completes (success or failure)
  requestPromise.finally(() => {
    requestCache.delete(key);
  });

  return requestPromise;
}

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
    "X-Requested-With": "XMLHttpRequest",
  },
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
  timeout: 10000,
});

// Add request interceptor to handle CSRF token
api.interceptors.request.use((config) => {
  const csrfToken = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];

  if (csrfToken) {
    config.headers["X-CSRFToken"] = csrfToken;
    config.headers["HTTP_X_CSRFTOKEN"] = csrfToken;
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
    console.error("Request error:", error);
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

    if (error.response?.status !== 403 || originalRequest._retry) {
      return Promise.reject(error);
    }

    const skipRetryEndpoints = [
      "/api/auth/login/",
      "/api/auth/register/",
      "/api/auth/csrf-token/",
    ];

    if (
      skipRetryEndpoints.some((endpoint) =>
        originalRequest.url?.includes(endpoint)
      )
    ) {
      return Promise.reject(error);
    }

    console.log("[API] CSRF token may be invalid, attempting to refresh...");
    originalRequest._retry = true;

    try {
      const csrfToken = await fetchCSRFToken();

      if (csrfToken) {
        originalRequest.headers["X-CSRFToken"] = csrfToken;
        originalRequest.headers["HTTP_X_CSRFTOKEN"] = csrfToken;
      }

      console.log("[API] Retrying original request with new CSRF token");
      return api(originalRequest);
    } catch (refreshError) {
      console.error("[API] Failed to refresh CSRF token:", refreshError);
      if (typeof window !== "undefined") {
        window.localStorage.removeItem("authState");
        window.location.href = "/login?session_expired=1";
      }
      return Promise.reject(refreshError);
    }
  }
);

// Function to get CSRF token from cookies (keep as fallback)
export function getCSRFToken(): string | null {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : null;
}

// Authentication state cache
let currentUserCache: Promise<User | null> | null = null;
let cacheTimestamp: number = 0;
const CACHE_DURATION = 5000; // 5 seconds cache

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

    const registrationData = {
      username: username.trim(),
      email: email.trim(),
      password: password,
      password2: password2,
      first_name: firstName.trim(),
      last_name: lastName.trim(),
    };

    // Create cache key for this registration request
    const cacheKey = createCacheKey(
      "POST",
      ENDPOINTS.AUTH.REGISTER,
      registrationData
    );

    // Check if same request is already in progress
    if (requestCache.has(cacheKey)) {
      console.log(
        "[API] Registration request already in progress, returning cached promise"
      );
      return requestCache.get(cacheKey);
    }

    const registrationPromise = (async () => {
      try {
        const csrfToken = await fetchCSRFToken();
        console.log("CSRF token for registration:", csrfToken);

        console.log("Registration data:", {
          ...registrationData,
          password: "***",
        });

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

        console.log("Registration response:", {
          status: response.status,
          headers: response.headers,
          data: response.data,
        });

        if (response.status === 201 || response.status === 200) {
          console.log("Registration successful, attempting auto-login...");

          try {
            console.log("Initiating auto-login after registration");
            const loginResponse = await this.login(username, password);
            console.log("Auto-login successful:", loginResponse);
            return loginResponse;
          } catch (loginError) {
            console.warn("Auto-login after registration failed:", loginError);
            return response.data;
          }
        } else {
          console.error(
            "Registration failed with status:",
            response.status,
            response.data
          );
          const errorMessage =
            (response.data as any)?.detail ||
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
    })();

    return cacheRequest(cacheKey, registrationPromise);
  },

  async login(username: string, password: string): Promise<AuthResponse> {
    const loginData = { username, password };
    const cacheKey = createCacheKey("POST", ENDPOINTS.AUTH.LOGIN, loginData);

    // Check if same login request is already in progress
    if (requestCache.has(cacheKey)) {
      console.log(
        "[API] Login request already in progress, returning cached promise"
      );
      return requestCache.get(cacheKey);
    }

    const loginPromise = (async () => {
      try {
        const csrfToken = await fetchCSRFToken();

        const response = await api.post(ENDPOINTS.AUTH.LOGIN, loginData, {
          headers: {
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
          validateStatus: (status) => status < 500,
        });

        console.log("Login response:", {
          status: response.status,
          data: response.data,
          headers: response.headers,
        });

        if (response.status === 200) {
          const hasSession = document.cookie.includes("sessionid");
          console.log("Login successful. Session cookie present:", hasSession);

          // Clear current user cache on successful login
          currentUserCache = null;
          cacheTimestamp = 0;

          return response.data.user || response.data;
        } else {
          const errorMessage = response.data?.message || "Login failed";
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
    })();

    return cacheRequest(cacheKey, loginPromise);
  },

  async logout(): Promise<void> {
    const cacheKey = createCacheKey("POST", ENDPOINTS.AUTH.LOGOUT, {});

    // Check if logout request is already in progress
    if (requestCache.has(cacheKey)) {
      console.log(
        "[API] Logout request already in progress, returning cached promise"
      );
      return requestCache.get(cacheKey);
    }

    const logoutPromise = (async () => {
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

        console.log("Logout response:", {
          status: response.status,
          data: response.data,
          headers: response.headers,
        });

        if (response.status !== 200) {
          const errorMessage = response.data?.message || "Logout failed";
          throw new Error(errorMessage);
        }

        // Clear caches on successful logout
        localStorage.removeItem("user");
        currentUserCache = null;
        cacheTimestamp = 0;
        requestCache.clear();
      } catch (error) {
        console.error("Logout error:", error);
        localStorage.removeItem("user");
        currentUserCache = null;
        cacheTimestamp = 0;
        throw error;
      }
    })();

    return cacheRequest(cacheKey, logoutPromise);
  },

  async getCurrentUser(): Promise<User | null> {
    const now = Date.now();

    // Return cached result if it's still valid
    if (currentUserCache && now - cacheTimestamp < CACHE_DURATION) {
      console.log("[API] Returning cached current user");
      return currentUserCache;
    }

    // Check if request is already in progress
    const cacheKey = createCacheKey("GET", ENDPOINTS.AUTH.USER);
    if (requestCache.has(cacheKey)) {
      console.log(
        "[API] getCurrentUser request already in progress, returning cached promise"
      );
      return requestCache.get(cacheKey);
    }

    const userPromise = (async () => {
      try {
        const response = await api.get(ENDPOINTS.AUTH.USER, {
          withCredentials: true,
          validateStatus: (status) => status < 500,
        });

        console.log("Current user response:", {
          status: response.status,
          data: response.data,
          headers: response.headers,
        });

        if (response.status === 200) {
          return response.data.user || response.data;
        }

        return null;
      } catch (error) {
        console.error("Error fetching current user:", error);
        return null;
      }
    })();

    // Cache the promise and timestamp
    currentUserCache = cacheRequest(cacheKey, userPromise);
    cacheTimestamp = now;

    return currentUserCache;
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

  // Method to clear all caches (useful for testing or manual cache invalidation)
  clearCache(): void {
    requestCache.clear();
    currentUserCache = null;
    cacheTimestamp = 0;
    console.log("[API] All caches cleared");
  },
};

export default authService;
