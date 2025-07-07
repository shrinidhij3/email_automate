import axios from "axios";
import { API_BASE_URL, AUTH_BASE_URL, ENDPOINTS } from "../config/api";

interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
}

interface AuthResponse extends User {}

interface ErrorResponse {
  error?: string;
  [key: string]: any; // Allow for additional error fields
}

// Set up axios defaults
const api = axios.create({
  baseURL: API_BASE_URL, // Use API_BASE_URL as the base for all API requests
  withCredentials: true, // Important for sessions
  headers: {
    "Content-Type": "application/json",
  },
});

// Log the base URL being used
console.log("Auth Service - Base URL:", AUTH_BASE_URL);

// Add CSRF token to all requests
api.interceptors.request.use(async (config) => {
  // Don't add CSRF token for CSRF endpoint itself
  if (config.url?.endsWith("csrf/")) {
    return config;
  }

  // Only add CSRF token for mutating requests
  if (
    ["post", "put", "delete", "patch"].includes(
      config.method?.toLowerCase() || ""
    )
  ) {
    try {
      console.log("Fetching CSRF token...");
      // Use the CSRF endpoint from the config to ensure correct path
      const csrfUrl = ENDPOINTS.AUTH.CSRF;
      console.log("CSRF URL:", csrfUrl);
      const response = await axios.get(csrfUrl, {
        withCredentials: true,
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.data?.csrfToken) {
        console.log("CSRF token retrieved successfully");
        config.headers["X-CSRFToken"] = response.data.csrfToken;
      } else {
        console.warn("CSRF token not found in response", response.data);
      }
    } catch (error) {
      console.error("Failed to get CSRF token", error);
      // Don't throw here to allow the original request to proceed
      // The server will reject it if CSRF is required
    }
  }
  return config;
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => {
    console.log(
      "API Response:",
      response.config.url,
      response.status,
      response.data
    );
    return response;
  },
  (error) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error("API Error Response:", {
        url: error.config?.url,
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers,
      });
    } else if (error.request) {
      // The request was made but no response was received
      console.error("API Request Error:", {
        url: error.config?.url,
        message: "No response received",
        request: error.request,
      });
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error("API Setup Error:", error.message);
    }
    return Promise.reject(error);
  }
);

const authService: {
  login: (username: string, password: string) => Promise<AuthResponse>;
  register: (
    username: string,
    email: string,
    password: string,
    password2: string,
    firstName: string,
    lastName: string
  ) => Promise<AuthResponse>;
  getCurrentUser: () => Promise<User | null>;
  logout: () => Promise<void>;
  isAuthenticated: () => Promise<boolean>;
} = {
  async login(username: string, password: string): Promise<AuthResponse> {
    try {
      // Use the full endpoint path from config
      const endpoint = ENDPOINTS.AUTH.LOGIN;
      console.log("Attempting login at:", endpoint);
      const response = await api.post<AuthResponse>(endpoint, {
        username,
        password,
      });
      console.log("Login successful:", response.data);
      return response.data;
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        const errorData = error.response.data as ErrorResponse;
        const message = errorData?.error || "Login failed";
        throw new Error(message);
      }
      throw new Error("Network error during login");
    }
  },

  async register(
    username: string,
    email: string,
    password: string,
    password2: string,
    firstName: string = "",
    lastName: string = ""
  ): Promise<AuthResponse> {
    try {
      // Use the full endpoint path from config
      const registerEndpoint = ENDPOINTS.AUTH.REGISTER;
      console.log("Attempting user registration at:", registerEndpoint);

      // First, register the user
      const registerResponse = await api.post<AuthResponse>(registerEndpoint, {
        username,
        email,
        password,
        password2,
        first_name: firstName,
        last_name: lastName,
      });

      console.log("Registration successful:", registerResponse.data);
      
      // After successful registration, log the user in
      try {
        console.log("Attempting to log in after registration...");
        const loginResponse = await this.login(username, password);
        console.log("Login after registration successful:", loginResponse);
        return loginResponse;
      } catch (loginError) {
        console.error("Login after registration failed:", loginError);
        // Even if login fails, return the registration response
        return registerResponse.data;
      }
    } catch (error: unknown) {
      console.error("Registration error:", error);

      if (axios.isAxiosError(error)) {
        const statusCode = error.response?.status;
        console.error(`Registration error status: ${statusCode}`);

        if (error.response?.data) {
          console.error("Error details:", error.response.data);
          const errorData = error.response.data as any;

          // Handle 400 Bad Request with detailed error messages
          if (statusCode === 400) {
            // Handle field-specific errors
            const fieldErrors = [];
            for (const [field, messages] of Object.entries(errorData)) {
              if (Array.isArray(messages)) {
                fieldErrors.push(`${field}: ${messages[0]}`);
              } else if (typeof messages === "string") {
                fieldErrors.push(`${field}: ${messages}`);
              } else if (field === "non_field_errors") {
                fieldErrors.push(messages);
              }
            }

            if (fieldErrors.length > 0) {
              throw new Error(fieldErrors.join("\n"));
            }

            // Fallback for other 400 errors
            throw new Error(
              "Invalid registration data. Please check your input."
            );
          }

          // Handle 500 Internal Server Error
          if (statusCode === 500) {
            throw new Error(
              "Server error during registration. Please try again later."
            );
          }

          // Handle other error statuses
          const message =
            errorData?.error ||
            errorData?.detail ||
            `Registration failed with status ${error.response.status}`;
          throw new Error(message);
        }
      }

      // Handle network errors
      console.error("Network error during registration:", error);
      throw new Error(
        "Network error during registration. Please check your connection."
      );
    }
  },

  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await api.get<{ isAuthenticated: boolean } & User>(
        ENDPOINTS.AUTH.SESSION
      );
      return response.data.isAuthenticated
        ? {
            id: response.data.id,
            username: response.data.username,
            email: response.data.email,
          }
        : null;
    } catch (error) {
      console.error("Error getting current user:", error);
      return null;
    }
  },

  async logout(): Promise<void> {
    try {
      await api.post(ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      console.error("Error during logout:", error);
    }
  },

  async isAuthenticated(): Promise<boolean> {
    try {
      // First try to get the current user
      const user = await this.getCurrentUser();
      return user !== null;
    } catch (error) {
      console.warn("getCurrentUser check failed, falling back to session check:", error);
      
      // Fallback to session check if getCurrentUser fails
      try {
        const response = await api.get<{ isAuthenticated: boolean }>(ENDPOINTS.AUTH.SESSION);
        return response.data.isAuthenticated === true;
      } catch (sessionError) {
        console.error("Session check failed:", sessionError);
        return false;
      }
    }
  },
};

export default authService;
