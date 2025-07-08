import api from "../api/api";
import { ENDPOINTS } from "../config/api";
import { AxiosError } from "axios";

// Add missing variable declarations
let currentUserCache: Promise<User> | null = null;
let cacheTimestamp: number = 0;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Define the AuthService interface
interface AuthService {
  register(
    username: string,
    email: string,
    password: string,
    password2: string,
    firstName?: string,
    lastName?: string
  ): Promise<User>;
  login(username: string, password: string): Promise<User>;
  logout(): Promise<void>;
  getCurrentUser(forceRefresh?: boolean): Promise<User | null>;
  isAuthenticated(): Promise<boolean>;
  clearCache(): void;
  getCSRFToken: () => Promise<string>;
}

// Add a small delay to prevent race conditions
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthSuccessResponse {
  user: User;
  message?: string;
}

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

// Cache for CSRF token
const csrfCache = {
  token: null as string | null,
  promise: null as Promise<string> | null,
  clear() {
    this.token = null;
    this.promise = null;
  },
};

export async function getCSRFToken(): Promise<string> {
  if (csrfCache.token) return csrfCache.token;

  if (csrfCache.promise) return csrfCache.promise;

  csrfCache.promise = (async () => {
    try {
      const response = await api.get<{ csrfToken: string }>(
        ENDPOINTS.AUTH.CSRF
      );
      csrfCache.token = response.data.csrfToken;
      return csrfCache.token;
    } catch (error) {
      csrfCache.promise = null;
      throw error;
    }
  })();
  return csrfCache.promise;
}

// Helper function to handle API errors
function handleApiError(error: unknown): Promise<never> {
  if (error instanceof AxiosError) {
    const message = error.response?.data?.error || error.message;
    console.error("API Error:", {
      message,
      status: error.response?.status,
      url: error.config?.url,
      method: error.config?.method,
    });
    return Promise.reject(new Error(message || "An unknown error occurred"));
  }
  console.error("Unexpected error:", error);
  return Promise.reject(new Error("An unexpected error occurred"));
}

// Auth service implementation - FIXED VERSION
const authService: AuthService = {
  async register(
    username: string,
    email: string,
    password: string,
    password2: string,
    firstName: string = "",
    lastName: string = ""
  ): Promise<User> {
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
        await getCSRFToken();

        console.log("Registration data:", {
          ...registrationData,
          password: "***",
        });

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

        currentUserCache = null;
        cacheTimestamp = 0;

        const responseData = response.data;

        if (response.data?.user) {
          return responseData.user;
        }

        if (responseData.id && responseData.username) {
          return responseData as unknown as User;
        }

        console.error("Unexpected registration response format:", responseData);
        throw new Error("Invalid response format from server");
      } catch (error) {
        // Handle the error and ensure we maintain the Promise<User> return type
        return handleApiError(error).catch(error => {
          // Re-throw the error to maintain the Promise<User> type
          throw error;
        }) as Promise<User>;
      }
    })();

    return cacheRequest(cacheKey, registrationPromise as Promise<User>);
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

        await delay(100);

        const csrfToken = await getCSRFToken();

        const response = await api.post<AuthSuccessResponse>(
          ENDPOINTS.AUTH.LOGIN,
          { username, password },
          {
            headers: {
              "Content-Type": "application/json",
              "X-Requested-With": "XMLHttpRequest",
              "X-CSRFToken": csrfToken,
            },
            withCredentials: true,
          }
        );

        if (response.data?.user) {
          const user = response.data.user;
          currentUserCache = Promise.resolve(user);
          cacheTimestamp = Date.now();
          return user;
        }

        throw new Error("Invalid response from server");
      } catch (error) {
        currentUserCache = null;
        cacheTimestamp = 0;

        if (error instanceof AxiosError && error.response?.status === 403) {
          csrfCache.clear();
        }

        return handleApiError(error);
      }
    })();

    return cacheRequest(cacheKey, loginPromise);
  },

  // FIXED LOGOUT METHOD - Single definition with comprehensive cleanup
  async logout(): Promise<void> {
    try {
      console.log("[Auth] Starting logout process");
      const csrfToken = await getCSRFToken();
      
      // Clear all caches before making the logout request
      this.clearCache();
      
      // Make logout request to server
      await api.post(
        ENDPOINTS.AUTH.LOGOUT,
        {},
        {
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        }
      );
      
      console.log("[Auth] Logout request successful");
    } catch (error) {
      console.error("Logout API error:", error);
      // Even if the server request fails, we still want to clear local state
    } finally {
      // Clear all local storage
      if (typeof window !== "undefined") {
        localStorage.clear(); // Clear all localStorage
        sessionStorage.clear();
      }
      
      // Clear all caches again to be safe
      this.clearCache();
      
      // Clear any service worker caches if they exist
      if ('caches' in window) {
        caches.keys().then(cacheNames => {
          cacheNames.forEach(cacheName => {
            caches.delete(cacheName);
          });
        });
      }
      
      console.log("[Auth] Logout cleanup completed");
    }
  },

  // FIXED GETCURRENTUSER METHOD - Single definition with proper error handling
  async getCurrentUser(forceRefresh = false): Promise<User | null> {
    const now = Date.now();

    // Return cached user if available and not expired
    if (
      currentUserCache &&
      !forceRefresh &&
      now - cacheTimestamp < CACHE_DURATION
    ) {
      try {
        return await currentUserCache;
      } catch (error) {
        console.error("Error getting cached user:", error);
        currentUserCache = null;
        cacheTimestamp = 0;
      }
    }

    try {
      await getCSRFToken();

      const response = await api.get<AuthSuccessResponse>(ENDPOINTS.AUTH.USER, {
        withCredentials: true,
        headers: {
          "Cache-Control": "no-cache",
          Pragma: "no-cache",
        },
      });

      if (response.data?.user) {
        const user = response.data.user;
        currentUserCache = Promise.resolve(user);
        cacheTimestamp = now;
        return user;
      }

      return null;
    } catch (error) {
      if (
        error instanceof AxiosError &&
        [401, 403].includes(error.response?.status || 0)
      ) {
        currentUserCache = null;
        cacheTimestamp = 0;

        if (error.response?.status === 403) {
          csrfCache.clear();
        }

        return null;
      }

      console.error("Error fetching current user:", error);
      return null;
    }
  },

  async isAuthenticated(forceRefresh = true): Promise<boolean> {
    try {
      // Force a fresh check by default to ensure we don't use cached data
      const user = await this.getCurrentUser(forceRefresh);
      return !!user;
    } catch (error) {
      console.error("Authentication check failed:", error);
      return false;
    }
  },

  // ENHANCED CACHE CLEARING
  clearCache(): void {
    currentUserCache = null;
    cacheTimestamp = 0;
    requestCache.clear();
    csrfCache.clear();
    console.log("[Auth] All caches cleared");
  },

  // Re-export getCSRFToken for external use
  getCSRFToken,
};

// Add cache clear method to getCSRFToken
getCSRFToken.cacheClear = () => {
  csrfCache.clear();
};

export default authService;
