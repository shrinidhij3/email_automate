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

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
    "X-Requested-With": "XMLHttpRequest",
  },
});

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
      // Use the dedicated CSRF token function
      const csrfToken = await fetchCSRFToken();

      const registrationData = {
        username: username.trim(),
        email: email.trim(),
        password: password,
        password2: password2,
        first_name: firstName.trim(),
        last_name: lastName.trim(),
      };

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

      if (response.status === 201 || response.status === 200) {
        console.log("Registration successful:", response.data);

        // After successful registration, try to log the user in
        try {
          const loginResponse = await this.login(username, password);
          return loginResponse;
        } catch (loginError) {
          console.warn("Auto-login after registration failed:", loginError);
          return response.data;
        }
      } else {
        throw new Error(`Registration failed with status: ${response.status}`);
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
      // Use the dedicated CSRF token function
      const csrfToken = await fetchCSRFToken();

      const response = await api.post<AuthResponse>(
        ENDPOINTS.AUTH.LOGIN,
        { username, password },
        {
          headers: {
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        }
      );

      return response.data;
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

      await api.post(
        ENDPOINTS.AUTH.LOGOUT,
        {},
        {
          headers: {
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        }
      );
    } catch (error) {
      console.error("Logout error:", error);
      throw error;
    }
  },

  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await api.get<User>(ENDPOINTS.AUTH.USER, {
        withCredentials: true,
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching current user:", error);
      return null;
    }
  },

  async isAuthenticated(): Promise<boolean> {
    try {
      const response = await api.get<{ isAuthenticated: boolean }>(
        ENDPOINTS.AUTH.SESSION
      );
      return response.data.isAuthenticated;
    } catch (error) {
      console.error("Error checking authentication status:", error);
      return false;
    }
  },
};

export default authService;
