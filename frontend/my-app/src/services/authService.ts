import api from "../api/api";
import { ENDPOINTS } from "../config/api";
import { AxiosError } from "axios";

// Add missing variable declarations
let currentUserCache: Promise<User> | null = null;
let cacheTimestamp: number = 0;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Define the AuthService interface
interface AuthService {
  login(username: string, password: string): Promise<AuthSuccessResponse>;
  register(userData: RegisterData): Promise<AuthSuccessResponse>;
  logout(): Promise<void>;
  getCurrentUser(forceRefresh?: boolean): Promise<User | null>;
  isAuthenticated(): Promise<boolean>;
  clearCache(): void;
  storeTokens(accessToken: string, refreshToken: string): void;
  clearTokens(): void;
}

// Remove unused delay, createCacheKey, cacheRequest, handleApiError

export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthSuccessResponse {
  user: User;
  access_token: string;
  refresh_token: string;
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

// Helper function to cache requests
function cacheRequest<T>(key: string, requestPromise: Promise<T>): Promise<T> {
  requestCache.set(key, requestPromise);
  requestPromise.finally(() => requestCache.delete(key));
  return requestPromise;
}

// Secure token storage functions
const TOKEN_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
};

// Auth service implementation - ENHANCED VERSION
const authService: AuthService = {
  async login(username: string, password: string): Promise<AuthSuccessResponse> {
    try {
      const response = await api.post<AuthSuccessResponse>(ENDPOINTS.AUTH.LOGIN, {
        username,
        password,
      });

      if (response.data?.access_token && response.data?.refresh_token) {
        this.storeTokens(response.data.access_token, response.data.refresh_token);
        this.clearCache(); // Clear cache on new login
      }

      return response.data;
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    }
  },

  async register(userData: RegisterData): Promise<AuthSuccessResponse> {
    try {
      const response = await api.post<AuthSuccessResponse>(ENDPOINTS.AUTH.REGISTER, userData);

      if (response.data?.access_token && response.data?.refresh_token) {
        this.storeTokens(response.data.access_token, response.data.refresh_token);
        this.clearCache(); // Clear cache on new registration
      }

      return response.data;
    } catch (error) {
      console.error("Registration error:", error);
      throw error;
    }
  },

  async logout(): Promise<void> {
    try {
      console.log("[Auth] Starting logout process");
      
      // Clear all caches before making the logout request
      this.clearCache();
      
      // Get refresh token for logout request
      const refreshToken = localStorage.getItem(TOKEN_KEYS.REFRESH_TOKEN);
      
      // Make logout request to server
      await api.post(
        ENDPOINTS.AUTH.LOGOUT,
        { refresh_token: refreshToken },
        {
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
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
      this.clearTokens();
      
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
        return null;
      }

      console.error("Error fetching current user:", error);
      return null;
    }
  },

  async isAuthenticated(forceRefresh = false): Promise<boolean> {
    try {
      // Check if we have tokens first
      const accessToken = localStorage.getItem(TOKEN_KEYS.ACCESS_TOKEN);
      if (!accessToken) {
        return false;
      }

      // Only force refresh if explicitly requested
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
    console.log("[Auth] All caches cleared");
  },

  // Secure token storage
  storeTokens(accessToken: string, refreshToken: string): void {
    try {
      localStorage.setItem(TOKEN_KEYS.ACCESS_TOKEN, accessToken);
      localStorage.setItem(TOKEN_KEYS.REFRESH_TOKEN, refreshToken);
      console.log("[Auth] Tokens stored securely");
    } catch (error) {
      console.error("Error storing tokens:", error);
    }
  },

  clearTokens(): void {
    try {
      localStorage.removeItem(TOKEN_KEYS.ACCESS_TOKEN);
      localStorage.removeItem(TOKEN_KEYS.REFRESH_TOKEN);
      console.log("[Auth] Tokens cleared");
    } catch (error) {
      console.error("Error clearing tokens:", error);
    }
  },
};

export default authService;
