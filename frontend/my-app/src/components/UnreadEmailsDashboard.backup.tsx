import React, { useState, useRef, useEffect } from "react";
import type { ChangeEvent, FormEvent } from "react";
import axios from "axios";
import type { AxiosProgressEvent } from "axios";
import "./UnreadEmailsDashboard.css";

interface EmailFormData {
  name: string;
  email: string;
  password: string;
  provider: string;
  files: FileList | null;
  imap_host: string;
  imap_port: number | string;
  smtp_host: string;
  smtp_port: number | string;
  notes: string;
  is_processed: boolean;
  secure: boolean;
  use_ssl: boolean;
}

// EmailApiError interface is kept for future use
// interface EmailApiError {
//   message: string;
//   errors?: Record<string, string[]>;
// }

// Error Boundary Component
interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error("Error Boundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="error-boundary">
            <h2>Something went wrong.</h2>
            <p>{this.state.error?.message}</p>
            <button onClick={() => this.setState({ hasError: false })}>
              Try again
            </button>
          </div>
        )
      );
    }
    return this.props.children;
  }
}

const UnreadEmailsDashboard = () => {
  // Form state
  const [formData, setFormData] = useState<EmailFormData>({
    name: "",
    email: "",
    password: "",
    provider: "gmail",
    files: null,
    imap_host: "imap.gmail.com",
    imap_port: 993,
    smtp_host: "smtp.gmail.com",
    smtp_port: 587,
    notes: "Use App Password with 2FA is enabled",
    is_processed: false,
    secure: true,
    use_ssl: true,
  });
  const [customProvider, setCustomProvider] = useState("");

  // UI state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [csrfToken, setCsrfToken] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Refs and constants
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://email-automate-ob1a.onrender.com';
  const AUTH_BASE_URL = `${API_BASE_URL}/api/auth/`;
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isMounted = useRef(true);
  // Removed unused navigate hook since it's not currently used
  // const navigate = useNavigate();

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  // Fetch CSRF token on component mount
  useEffect(() => {
    const fetchCsrf = async () => {
      try {
        console.log("Fetching CSRF token...");
        const response = await axios.get(`${AUTH_BASE_URL}csrf/`, {
          withCredentials: true,
          headers: {
            Accept: "application/json",
          },
        });

        if (response.data.csrfToken) {
          setCsrfToken(response.data.csrfToken);
          axios.defaults.headers.common["X-CSRFToken"] =
            response.data.csrfToken;
        }
      } catch (error) {
        console.error("Error fetching CSRF token:", error);
      }
    };

    fetchCsrf();
  }, []);

  // Get CSRF token from cookies
  const getCsrfToken = (): string | null => {
    const cookieValue = document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="))
      ?.split("=")[1];
    return cookieValue || null;
  };

  // Handle custom provider change
  const handleCustomProviderChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setCustomProvider(value);
    // Only update the form data when the input changes, not on every keystroke
  };

  // Handle provider change
  const handleProviderChange = (e: ChangeEvent<HTMLSelectElement>) => {
    const { value } = e.target;

    if (value === "other") {
      // Clear server config fields when 'Other' is selected
      setFormData((prev) => ({
        ...prev,
        provider: "custom",
        imap_host: "",
        imap_port: "",
        smtp_host: "",
        smtp_port: "",
        secure: false,
        use_ssl: false,
        notes: "",
      }));
    } else {
      // Set default values for known providers
      const defaults = {
        gmail: {
          imap_host: "imap.gmail.com",
          imap_port: 993,
          smtp_host: "smtp.gmail.com",
          smtp_port: 587,
          secure: true,
          use_ssl: true,
          notes: "Use App Password with 2FA enabled",
        },
      };

      setFormData((prev) => ({
        ...prev,
        provider: value,
        ...(defaults[value as keyof typeof defaults] || {}),
      }));
    }
  };

  // Handle form input changes
  const handleInputChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;

    // Clear any previous errors for this field
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Handle file input changes
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFormData((prev) => ({
        ...prev,
        files: e.target.files,
      }));
    }
  };

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = "Name is required";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email is invalid";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    }

    // If provider is other, validate custom provider and server config
    if (formData.provider === "other" || formData.provider === "custom") {
      if (!customProvider.trim()) {
        newErrors.customProvider = "Custom provider name is required";
      }
      if (!formData.imap_host) newErrors.imap_host = "IMAP Host is required";
      if (!formData.imap_port) newErrors.imap_port = "IMAP Port is required";
      if (!formData.smtp_host) newErrors.smtp_host = "SMTP Host is required";
      if (!formData.smtp_port) newErrors.smtp_port = "SMTP Port is required";
    }

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    // Prevent default form submission
    e.preventDefault();
    e.stopPropagation();

    // If using custom provider, update the provider value before submission
    if (formData.provider === "custom" || formData.provider === "other") {
      setFormData((prev) => ({
        ...prev,
        provider: customProvider.trim() || "custom",
      }));
    }

    // Validate form
    if (!validateForm()) {
      return;
    }

    // Reset any previous errors
    setSubmitError(null);

    // Set loading state
    setIsSubmitting(true);

    try {
      // Ensure we have a CSRF token
      const currentCsrfToken = csrfToken || getCsrfToken();
      if (!currentCsrfToken) {
        throw new Error("CSRF token not found");
      }

      // Create FormData for the request
      const formDataObj = new FormData();

      // Add all form fields to FormData
      Object.entries(formData).forEach(([key, value]) => {
        if (key !== "files" && value !== null && value !== undefined) {
          formDataObj.append(key, String(value));
        }
      });

      // Add files if any
      if (formData.files) {
        Array.from(formData.files).forEach((file) => {
          formDataObj.append("files", file);
        });
      }

      // Submit the form data
      const response = await axios.post(
        `${API_BASE_URL}unread-emails/submissions/`,
        formDataObj,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            "X-CSRFToken": currentCsrfToken,
          },
          withCredentials: true,
        }
      );

      const unreadEmailId = response.data.id;
      console.log("Created unread email record:", unreadEmailId);

      // Handle file uploads if any
      if (formData.files && formData.files.length > 0) {
        console.log(`Uploading ${formData.files.length} file(s)`);

        await Promise.all(
          Array.from(formData.files).map(async (file) => {
            if (!isMounted.current) return null;

            try {
              const fileFormData = new FormData();
              fileFormData.append("file", file);
              fileFormData.append("original_filename", file.name);
              fileFormData.append(
                "content_type",
                file.type || "application/octet-stream"
              );

              const uploadUrl = `${API_BASE_URL}unread-emails/submissions/${unreadEmailId}/upload_attachment/`;

              console.log(
                `Uploading ${file.name} (${(file.size / 1024).toFixed(2)} KB)`
              );

              const uploadResponse = await axios.post(uploadUrl, fileFormData, {
                headers: {
                  "Content-Type": "multipart/form-data",
                  "X-CSRFToken": currentCsrfToken,
                },
                withCredentials: true,
                onUploadProgress: (progressEvent: AxiosProgressEvent) => {
                  if (!isMounted.current) return;
                  const total = progressEvent.total || 1;
                  const loaded = progressEvent.loaded || 0;
                  const progress = Math.round((loaded * 100) / total);
                  console.log(`Upload progress for ${file.name}: ${progress}%`);
                },
              });

              if (!isMounted.current) return null;

              console.log(
                `File ${file.name} uploaded successfully:`,
                uploadResponse.data
              );
              return uploadResponse.data;
            } catch (uploadError) {
              console.error(`Error uploading file ${file.name}:`, uploadError);
              return {
                error: true,
                file: file.name,
                message:
                  uploadError instanceof Error
                    ? uploadError.message
                    : "Unknown error",
              };
            }
          })
        );
      }

      // Success!
      setIsSubmitted(true);

      // Reset form
      setFormData({
        name: "",
        email: "",
        password: "",
        provider: "gmail",
        files: null,
        imap_host: "imap.gmail.com",
        imap_port: 993,
        smtp_host: "smtp.gmail.com",
        smtp_port: 587,
        notes: "Use App Password with 2FA is enabled",
        is_processed: false,
        secure: true,
        use_ssl: true,
      });

      // Reset custom provider
      setCustomProvider("");

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      console.error("Submission error:", error);

      if (axios.isAxiosError(error)) {
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          console.error("Error response data:", error.response.data);
          console.error("Error status:", error.response.status);
          console.error("Error headers:", error.response.headers);

          if (error.response.data) {
            setSubmitError(
              error.response.data.detail ||
                error.response.data.message ||
                "An error occurred while submitting the form."
            );
          } else {
            setSubmitError(
              `Server responded with status ${error.response.status}`
            );
          }
        } else if (error.request) {
          // The request was made but no response was received
          console.error("No response received:", error.request);
          setSubmitError("No response received from server. Please try again.");
        } else {
          // Something happened in setting up the request
          console.error("Request setup error:", error.message);
          setSubmitError(`Request error: ${error.message}`);
        }
      } else {
        // Non-Axios error
        const errorMessage =
          error instanceof Error ? error.message : "An unknown error occurred";
        setSubmitError(errorMessage);
      }
    } finally {
      if (isMounted.current) {
        setIsSubmitting(false);
      }
    }
  };

  // Render the form
  return (
    <div className="unread-emails-dashboard">
      <h1>Email Submission</h1>

      {isSubmitted ? (
        <div className="success-message">
          <h2>Thank you for your submission!</h2>
          <p>Your email information has been received successfully.</p>
          <button
            onClick={() => setIsSubmitted(false)}
            className="submit-button"
          >
            Submit Another
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="unread-emails-form">
          <div className="form-scroll-container">
            <div className="form-content">
              <div className="form-group">
                <label htmlFor="name">Name</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className={errors.name ? "error" : ""}
                />
                {errors.name && (
                  <span className="error-message">{errors.name}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className={errors.email ? "error" : ""}
                />
                {errors.email && (
                  <span className="error-message">{errors.email}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className={errors.password ? "error" : ""}
                />
                {errors.password && (
                  <span className="error-message">{errors.password}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="provider">Email Provider</label>
                <select
                  id="provider"
                  name="provider"
                  value={
                    formData.provider === "custom" ? "other" : formData.provider
                  }
                  onChange={handleProviderChange}
                >
                  <option value="gmail">Gmail</option>
                  <option value="other">Other (Custom SMTP/IMAP)</option>
                </select>

                {formData.provider === "other" ||
                formData.provider === "custom" ? (
                  <div className="form-group" style={{ marginTop: "1rem" }}>
                    <label htmlFor="customProvider">Custom Provider Name</label>
                    <input
                      type="text"
                      id="customProvider"
                      name="customProvider"
                      value={customProvider}
                      onChange={handleCustomProviderChange}
                      placeholder="e.g., mycompany-mail"
                      className={errors.customProvider ? "error" : ""}
                    />
                    {errors.customProvider && (
                      <span className="error-message">
                        {errors.customProvider}
                      </span>
                    )}
                    <p className="help-text">
                      Enter a name for your custom email provider
                    </p>
                  </div>
                ) : (
                  <p className="help-text">
                    Using default settings for {formData.provider}
                  </p>
                )}
              </div>

              {/* Server Configuration Section */}
              <div className="server-config-section">
                <h3>Server Configuration</h3>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="imap_host">IMAP Host</label>
                    <input
                      type="text"
                      id="imap_host"
                      name="imap_host"
                      value={formData.imap_host}
                      onChange={handleInputChange}
                      disabled={formData.provider !== "other"}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="imap_port">IMAP Port</label>
                    <input
                      type="number"
                      id="imap_port"
                      name="imap_port"
                      value={formData.imap_port}
                      onChange={handleInputChange}
                      disabled={formData.provider !== "other"}
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="smtp_host">SMTP Host</label>
                    <input
                      type="text"
                      id="smtp_host"
                      name="smtp_host"
                      value={formData.smtp_host}
                      onChange={handleInputChange}
                      disabled={formData.provider !== "other"}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="smtp_port">SMTP Port</label>
                    <input
                      type="number"
                      id="smtp_port"
                      name="smtp_port"
                      value={formData.smtp_port}
                      onChange={handleInputChange}
                      disabled={formData.provider !== "other"}
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group checkbox-group">
                    <input
                      type="checkbox"
                      id="secure"
                      name="secure"
                      checked={formData.secure}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          secure: e.target.checked,
                        }))
                      }
                      disabled={formData.provider !== "other"}
                    />
                    <label htmlFor="secure">Use secure connection</label>
                  </div>

                  <div className="form-group checkbox-group">
                    <input
                      type="checkbox"
                      id="use_ssl"
                      name="use_ssl"
                      checked={formData.use_ssl}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          use_ssl: e.target.checked,
                        }))
                      }
                      disabled={formData.provider !== "other"}
                    />
                    <label htmlFor="use_ssl">Use SSL/TLS</label>
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="notes">Notes</label>
                  <textarea
                    id="notes"
                    name="notes"
                    value={formData.notes}
                    onChange={handleInputChange}
                    rows={3}
                    disabled={formData.provider !== "other"}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="files">Attachments (Optional)</label>
                <input
                  type="file"
                  id="files"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  multiple
                />
                {formData.files && formData.files.length > 0 && (
                  <div className="file-list">
                    <p>Selected files:</p>
                    <ul>
                      {Array.from(formData.files).map((file, index) => (
                        <li key={index}>
                          {file.name} ({(file.size / 1024).toFixed(2)} KB)
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {submitError && (
                <div className="error-message">{submitError}</div>
              )}
            </div>
          </div>

          <div className="form-actions">
              <button
                type="button"
                className="submit-button"
                disabled={isSubmitting}
                onClick={(e) => {
                  e.preventDefault();
                  const form = e.currentTarget.closest('form');
                  if (form) {
                    const submitEvent = new Event('submit', { cancelable: true });
                    form.dispatchEvent(submitEvent);
                  }
                }}
              >
                {isSubmitting ? "Submitting..." : "Submit"}
              </button>
          </div>
        </form>
      )}
    </div>
  );
};

// Wrap the component with ErrorBoundary
export default function UnreadEmailsDashboardWithErrorBoundary() {
  return (
    <ErrorBoundary>
      <UnreadEmailsDashboard />
    </ErrorBoundary>
  );
}
