import api, { getCSRFToken } from "../api/api";
import { ENDPOINTS } from "../config/api";
import { AxiosError } from "axios";

export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
}
// Define the shape of successful login/registration responses
export interface AuthSuccessResponse {
  user: User;
  message?: string;
}

// Define the shape of error responses
export interface AuthErrorResponse {
  error?: string;
  message?: string;
  [key: string]: any;
}


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
  requestPromise.finally(() => requestCache.delete(key));
  return requestPromise;
}

// Helper function to handle API errors
function handleApiError(error: unknown): never {
  if (error instanceof AxiosError) {
    const message = error.response?.data?.error || error.message;
    console.error("API Error:", {
      message,
      status: error.response?.status,
      url: error.config?.url,
      method: error.config?.method,
    });
    throw new Error(message || "An unknown error occurred");
  }
  console.error("Unexpected error:", error);
  throw new Error("An unexpected error occurred");
}

// Authentication state cache
let currentUserCache: Promise<User | null> | null = null;
let cacheTimestamp: number = 0;
const CACHE_DURATION = 30000; // 30 seconds cache

const authService = {
  async register(
    username: string,
    email: string,
    password: string,
    password2: string,
    firstName: string = "",
    lastName: string = ""
  ): Promise<User> {
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

    const cacheKey = createCacheKey(
      "POST",
      ENDPOINTS.AUTH.REGISTER,
      registrationData
    );

    if (requestCache.has(cacheKey)) {
      console.log("[Auth] Registration request already in progress");
      return requestCache.get(cacheKey)!;
    }

    const registrationPromise = (async () => {
      try {
        // Get CSRF token before registration
        await getCSRFToken();

        console.log("Registration data:", {
          ...registrationData,
          password: "***",
        });

        // Define the expected response type for the registration endpoint
        interface RegisterResponse {
          user?: User;
          message?: string;
          [key: string]: any;
        }

        const response = await api.post<RegisterResponse>(
          ENDPOINTS.AUTH.REGISTER,
          registrationData,
          {
            headers: {
              "Content-Type": "application/json",
              "X-Requested-With": "XMLHttpRequest",
            },
            withCredentials: true,
          }
        );

        console.log("Registration response:", {
          status: response.status,
          data: response.data,
        });

        // Clear any cached user data
        currentUserCache = null;

        const responseData = response.data;

        // If the response has a user property, return the user
        if (responseData.user) {
          return responseData.user;
        }

        // If response is a User object directly
        if (responseData.id && responseData.username) {
          return responseData as unknown as User;
        }

        // If we get here, the response format is unexpected
        console.error("Unexpected registration response format:", responseData);
        throw new Error("Invalid response format from server");
      } catch (error) {
        return handleApiError(error);
      }
    })();

    return cacheRequest(cacheKey, registrationPromise);
  },

  async login(username: string, password: string): Promise<User> {
    const cacheKey = createCacheKey("POST", ENDPOINTS.AUTH.LOGIN, { username });

    if (requestCache.has(cacheKey)) {
      console.log("[Auth] Login request already in progress");
      return requestCache.get(cacheKey)!;
    }

    const loginPromise = (async () => {
      try {
        console.log("[Auth] Login attempt for user:", username);

        // Get CSRF token before login
        await getCSRFToken();

        // Define the expected response type for the login endpoint
        interface LoginResponse {
          user?: User;
          message?: string;
          [key: string]: any;
        }

        const response = await api.post<LoginResponse>(
          ENDPOINTS.AUTH.LOGIN,
          { username, password },
          {
            headers: {
              "Content-Type": "application/json",
              "X-Requested-With": "XMLHttpRequest",
            },
            withCredentials: true,
          }
        );

        console.log("Login response:", {
          status: response.status,
          data: response.data,
          headers: response.headers,
        });

        if (response.status === 200) {
          console.log(
            "Login successful. Session cookie present:",
            document.cookie.includes("sessionid")
          );

          // Clear current user cache on successful login
          currentUserCache = null;
          cacheTimestamp = 0;

          const responseData = response.data;

          // If the response has a user property, return the user
          if (responseData.user) {
            return responseData.user;
          }

          // If response is a User object directly
          if (responseData.id && responseData.username) {
            return responseData as unknown as User;
          }

          // If we get here, the response format is unexpected
          console.error("Unexpected response format:", responseData);
          throw new Error("Invalid response format from server");
        } else {
          const errorData = response.data as {
            message?: string;
            error?: string;
          };
          throw new Error(
            errorData.message || errorData.error || "Login failed"
          );
        }
      } catch (error) {
        return handleApiError(error);
      }
    })();

    return cacheRequest(cacheKey, loginPromise);
  },

  async logout(): Promise<void> {
    try {
      await api.post(
        ENDPOINTS.AUTH.LOGOUT,
        {},
        {
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
          },
          withCredentials: true,
        }
      );

      // Clear any cached user data
      currentUserCache = null;

      // Clear any stored tokens or user data
      if (typeof window !== "undefined") {
        localStorage.removeItem("authState");
      }
    } catch (error) {
      // Even if logout fails, clear the local state
      currentUserCache = null;
      if (typeof window !== "undefined") {
        localStorage.removeItem("authState");
      }
      console.error("Logout error:", error);
      // Don't throw error for logout as we want to continue clearing state
    }
  },

  async getCurrentUser(forceRefresh = false): Promise<User | null> {
    const now = Date.now();

    // Return cached user if available and not expired, and not forcing refresh
    if (
      !forceRefresh &&
      currentUserCache &&
      now - cacheTimestamp < CACHE_DURATION
    ) {
      console.log("[Auth] Returning cached user data");
      return currentUserCache;
    }

    console.log("[Auth] Fetching current user from server");
    cacheTimestamp = now;

    currentUserCache = (async () => {
      try {
        const response = await api.get<User>(ENDPOINTS.AUTH.USER, {
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
          withCredentials: true,
        });

        return response.data;
      } catch (error) {
        console.error("Error fetching current user:", error);
        // Clear cache on error
        currentUserCache = null;
        return null;
      }
    })();

    return currentUserCache;
  },

  async isAuthenticated(): Promise<boolean> {
    try {
      const user = await authService.getCurrentUser();
      return !!user;
    } catch {
      return false;
    }
  },

  // Method to clear all caches (useful for testing or manual cache invalidation)
  clearCache(): void {
    currentUserCache = null;
    requestCache.clear();
    console.log("[Auth] All caches cleared");
  },

  // Helper to get CSRF token (re-exported from api.ts)
  getCSRFToken,
};

export default authService;
