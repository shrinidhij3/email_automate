// API Configuration for both development and production environments
const DEFAULT_LOCAL_BACKEND = "http://localhost:8000";
const PRODUCTION_BACKEND = "https://email-automate-ob1a.onrender.com";

// Get the base URL from environment variables or use defaults
const getBaseUrl = () => {
  // In production, use the production backend URL
  if (import.meta.env.PROD) {
    return PRODUCTION_BACKEND;
  }
  
  // In development, use the environment variable or default to local backend
  return import.meta.env.VITE_API_BASE_URL || DEFAULT_LOCAL_BACKEND;
};

const BASE_URL = getBaseUrl();

// Remove trailing slashes and ensure we don't have duplicate /api/
export const API_BASE_URL = BASE_URL.replace(/(\/)+$/, "");

// For backward compatibility
export const AUTH_BASE_URL = `${API_BASE_URL}/api/auth/`;

export const ENDPOINTS = {
  AUTH: {
    LOGIN: "/api/auth/login/",
    REGISTER: "/api/auth/register/",
    LOGOUT: "/api/auth/logout/",
    CSRF: "/api/auth/csrf-token/", // Updated to match backend
    SESSION: "/api/auth/session/",
    USER: "/api/auth/user/",
  },
  UNREAD_EMAILS: {
    SUBMISSIONS: "/api/unread-emails/submissions/",
    UPLOAD_ATTACHMENT: (id: string) =>
      `/api/unread-emails/submissions/${id}/upload_attachment/`,
  },
  CAMPAIGNS: {
    BASE: "/api/campaigns/",
    UPLOAD_ATTACHMENTS: (id: string) =>
      `/api/campaigns/${id}/upload_attachments/`,
  },
  EMAIL_ENTRIES: "/api/email-entries/",
  BULK_EMAIL_ENTRIES: "/api/email-entries/bulk/",
};

// Helper function to get full API URL
export const getApiUrl = (endpoint: string) => {
  // If the endpoint already starts with http, return as is
  if (endpoint.startsWith("http")) {
    return endpoint;
  }

  // Remove leading slashes from endpoint
  const cleanEndpoint = endpoint.replace(/^\/+/, "");

  // Combine base URL with endpoint, ensuring no duplicate /api/
  return `${API_BASE_URL}/${cleanEndpoint}`;
};
