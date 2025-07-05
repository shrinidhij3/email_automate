// API Configuration
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/";
export const AUTH_BASE_URL = `${API_BASE_URL}auth/`;

// Log the API configuration for debugging
console.log("API Configuration:", {
  API_BASE_URL,
  AUTH_BASE_URL,
  NODE_ENV: import.meta.env.MODE,
  VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
});

export const ENDPOINTS = {
  AUTH: {
    LOGIN: `${AUTH_BASE_URL}login/`,
    REGISTER: `${AUTH_BASE_URL}register/`,
    LOGOUT: `${AUTH_BASE_URL}logout/`,
    CSRF: `${AUTH_BASE_URL}csrf/`,
    SESSION: `${AUTH_BASE_URL}session/`,
  },
  UNREAD_EMAILS: {
    SUBMISSIONS: "unread-emails/submissions/",
    UPLOAD_ATTACHMENT: (id: string) =>
      `unread-emails/submissions/${id}/upload_attachment/`,
  },
  CAMPAIGNS: {
    BASE: "campaigns/",
    UPLOAD_ATTACHMENTS: (id: string) => `campaigns/${id}/upload_attachments/`,
  },
  EMAIL_ENTRIES: "email-entries/",
};

// Helper function to get full API URL
export const getApiUrl = (endpoint: string) => {
  // If the endpoint already starts with http, return as is
  if (endpoint.startsWith("http")) {
    return endpoint;
  }

  // If the endpoint starts with /api/, use the base URL without the /api/ part
  if (endpoint.startsWith("/api/")) {
    return `${API_BASE_URL.replace(/\/+$/, "")}${endpoint.replace(
      /^\/+api\//,
      ""
    )}`;
  }

  // Otherwise, append to the base URL
  return `${API_BASE_URL}${endpoint.replace(/^\/+/, "")}`;
};
