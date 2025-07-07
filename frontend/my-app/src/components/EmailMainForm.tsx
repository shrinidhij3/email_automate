import { useState, useEffect } from "react";
import "./EmailMain.css";
import axios from "axios";
import type { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from "axios";
import { API_BASE_URL } from "../config/api";
import { fetchCSRFToken } from "../utils/csrf";

// Create axios instance with base URL and CSRF configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest"
  },
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken'
});

// Request interceptor for logging
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Skip logging for GET requests or CSRF endpoint
    if (config.method?.toLowerCase() !== 'get' && !config.url?.includes('csrf-token')) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, {
        data: config.data,
        headers: config.headers
      });
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 403) {
      console.error('403 Forbidden - Possible CSRF token mismatch');
      // Optionally try to refresh the CSRF token and retry
      try {
        await fetchCSRFToken();
        return api(error.config);
      } catch (refreshError) {
        console.error('Failed to refresh CSRF token:', refreshError);
        window.location.href = '/login';  // Redirect to login on failure
      }
    }
    return Promise.reject(error);
  }
);


// Response interceptor for handling errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    console.error('API Error:', {
      message: error.message,
      status: error.response?.status,
      url: error.config?.url,
      method: error.config?.method,
    });

    // Handle 403 Forbidden (CSRF token might be invalid)
    if (error.response?.status === 403) {
      console.error('[AUTH] Authentication failed. Please log in again.');
      // Uncomment to enable auto-redirect to login
      // window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

interface ProviderConfig {
  imapHost: string;
  imapPort: string;
  smtpHost: string;
  smtpPort: string;
  useSecure: boolean;
  useSsl: boolean;
  notes: string;
}

interface EmailConfig {
  name: string;
  email: string;
  password: string;
  provider: string;
  customProvider: string;
  imapHost: string;
  imapPort: string;
  smtpHost: string;
  smtpPort: string;
  useSecure: boolean;
  useSsl: boolean;
  notes: string;
  files: File[];
}

const PROVIDER_CONFIGS: Record<string, ProviderConfig> = {
  gmail: {
    imapHost: "imap.gmail.com",
    imapPort: "993",
    smtpHost: "smtp.gmail.com",
    smtpPort: "587",
    useSecure: true,
    useSsl: true,
    notes: "Use App Password with 2FA enabled",
  },
  other: {
    imapHost: "",
    imapPort: "",
    smtpHost: "",
    smtpPort: "",
    useSecure: false,
    useSsl: false,
    notes: "",
  },
};

// Error handling is done through the error state and form validation

function EmailMainForm() {
  const [formData, setFormData] = useState<EmailConfig>({
    name: "",
    email: "",
    password: "",
    provider: "gmail",
    customProvider: "",
    imapHost: PROVIDER_CONFIGS.gmail.imapHost,
    imapPort: PROVIDER_CONFIGS.gmail.imapPort,
    smtpHost: PROVIDER_CONFIGS.gmail.smtpHost,
    smtpPort: PROVIDER_CONFIGS.gmail.smtpPort,
    useSecure: PROVIDER_CONFIGS.gmail.useSecure,
    useSsl: PROVIDER_CONFIGS.gmail.useSsl,
    notes: PROVIDER_CONFIGS.gmail.notes,
    files: [],
  });

  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [showHelp, setShowHelp] = useState<boolean>(false);
  const [fileNames, setFileNames] = useState<string[]>([]);
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);
  const totalSteps = 3;
  
  const isCustomProvider = formData.provider === "other";

  useEffect(() => {
    if (!isCustomProvider) {
      const providerConfig =
        PROVIDER_CONFIGS[formData.provider as keyof typeof PROVIDER_CONFIGS] ||
        {};
      setFormData((prev) => ({
        ...prev,
        ...providerConfig,
        customProvider: "",
      }));
    }
  }, [formData.provider, isCustomProvider, setFormData]);

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value, type, checked } = e.target as HTMLInputElement;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const provider = e.target.value;
    setFormData((prev) => ({
      ...prev,
      provider,
      ...(provider !== "other" &&
        PROVIDER_CONFIGS[provider as keyof typeof PROVIDER_CONFIGS]),
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setFormData((prev) => ({
        ...prev,
        files: [...prev.files, ...newFiles],
      }));
      setFileNames((prev) => [
        ...prev,
        ...newFiles.map((file: File) => file.name),
      ]);
    }
  };

  const removeFile = (index: number) => {
    const newFiles = [...formData.files];
    const newFileNames = [...fileNames];
    newFiles.splice(index, 1);
    newFileNames.splice(index, 1);
    setFormData((prev) => ({ ...prev, files: newFiles }));
    setFileNames(newFileNames);
  };

  const nextStep = () => {
    if (currentStep < totalSteps) setCurrentStep((prev) => prev + 1);
  };

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep((prev) => prev - 1);
  };

  const quickFillPort = (field: "imapPort" | "smtpPort", value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const validateForm = (): boolean => {
    // Reset error message
    setErrorMessage('');

    // Check required fields
    if (!formData.name.trim()) {
      setErrorMessage('Name is required');
      return false;
    }
    
    if (!formData.email.trim()) {
      setErrorMessage('Email is required');
      return false;
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      setErrorMessage('Please enter a valid email address');
      return false;
    }
    
    if (!formData.password) {
      setErrorMessage('Password is required');
      return false;
    }
    
    // Server settings validation (only for custom providers)
    if (isCustomProvider) {
      if (!formData.customProvider) {
        setErrorMessage('Custom provider name is required');
        return false;
      }
      
      if (!formData.imapHost?.trim()) {
        setErrorMessage('IMAP Host is required');
        return false;
      }
      
      if (!formData.imapPort?.trim()) {
        setErrorMessage('IMAP Port is required');
        return false;
      }
      
      if (!formData.smtpHost?.trim()) {
        setErrorMessage('SMTP Host is required');
        return false;
      }
      
      if (!formData.smtpPort?.trim()) {
        setErrorMessage('SMTP Port is required');
        return false;
      }
    }
    
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }
    
    setIsSubmitting(true);
    setErrorMessage('');
    
    try {
      // Create the main campaign data (without files)
      const campaignData = {
        name: formData.name.trim(),
        email: formData.email.trim(),
        password: formData.password,
        provider: isCustomProvider ? formData.customProvider : formData.provider,
        imap_host: formData.imapHost,
        imap_port: formData.imapPort ? parseInt(formData.imapPort, 10) : null,
        smtp_host: formData.smtpHost,
        smtp_port: formData.smtpPort ? parseInt(formData.smtpPort, 10) : null,
        use_ssl: formData.useSsl,
        notes: formData.notes || "",
      };

      console.log("Submitting campaign data:", {
        ...campaignData,
        password: '***', // Don't log the actual password
      });
      
      // Make the request using our configured api instance
      const apiResponse = await api.post('/api/campaigns/', campaignData, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
      });

      console.log('Response status:', apiResponse.status);
      console.log('Response headers:', apiResponse.headers);
      console.log('Response data:', apiResponse.data);
      
      if (apiResponse.status >= 400) {
        const errorDetail = apiResponse.data?.detail || 
                          apiResponse.data?.message || 
                          'No error details provided';
        console.error('Campaign creation failed:', {
          status: apiResponse.status,
          statusText: apiResponse.statusText,
          data: apiResponse.data,
          headers: apiResponse.headers
        });
        throw new Error(`Failed to create campaign: ${errorDetail}`);
      }
      
      console.log("Campaign created successfully:", apiResponse.data);
      
      // Reset form and show success message
      setFormData({
        name: "",
        email: "",
        password: "",
        provider: "gmail",
        customProvider: "",
        imapHost: PROVIDER_CONFIGS.gmail.imapHost,
        imapPort: PROVIDER_CONFIGS.gmail.imapPort,
        smtpHost: PROVIDER_CONFIGS.gmail.smtpHost,
        smtpPort: PROVIDER_CONFIGS.gmail.smtpPort,
        useSecure: PROVIDER_CONFIGS.gmail.useSecure,
        useSsl: PROVIDER_CONFIGS.gmail.useSsl,
        notes: "",
        files: [],
      });
      setFileNames([]);
      setCurrentStep(1);
      
      // Show success message
      setErrorMessage("Campaign created successfully!");
      
    } catch (error: any) {
      console.error("Campaign submission error:", error);
      
      // Handle API errors
      if (error?.response) {
        // Handle HTTP errors with response
        const errorMessage = error.response.data?.detail || 
                           error.response.data?.message || 
                           error.message || 
                           "Failed to create campaign";
        setErrorMessage(`Error: ${errorMessage}`);
      } else if (error?.request) {
        // The request was made but no response was received
        setErrorMessage("No response from server. Please check your connection.");
      } else if (error instanceof Error) {
        // Something happened in setting up the request
        setErrorMessage(`Error: ${error.message}`);
      } else {
        setErrorMessage("An unknown error occurred. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="form-step">
            <h3>Account Information</h3>
            <p className="form-instruction">
              Enter your basic account details. All fields are required.
            </p>
            <div className="form-group">
              <label htmlFor="name">Full Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="John Doe"
                className={errorMessage && !formData.name.trim() ? "error" : ""}
              />
              {errorMessage && !formData.name.trim() && (
                <span className="error-message">Name is required</span>
              )}
            </div>
            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="your.email@example.com"
                className={errorMessage && !formData.email.trim() ? "error" : ""}
              />
              {errorMessage && !formData.email.trim() && (
                <span className="error-message">Email is required</span>
              )}
            </div>
            <div className="form-group">
              <label htmlFor="password">Password *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="••••••••"
                className={errorMessage && !formData.password ? "error" : ""}
              />
              {errorMessage && !formData.password && (
                <span className="error-message">Password is required</span>
              )}
              <p className="help-text">
                Use an app password if 2FA is enabled on your email account
              </p>
            </div>
          </div>
        );
      case 2:
        return (
          <div className="form-step">
            <h3>Server Settings</h3>
            <p className="form-instruction">
              Configure your email server settings. We've pre-filled common
              values for popular providers.
            </p>
            <div className="form-group">
              <label htmlFor="provider">Email Provider</label>
              <select
                id="provider"
                name="provider"
                value={formData.provider}
                onChange={handleProviderChange}
              >
                <option value="gmail">Gmail</option>
                <option value="outlook">Outlook/Office 365</option>
                <option value="yahoo">Yahoo Mail</option>
                <option value="other">Other IMAP/SMTP</option>
              </select>
            </div>
            {isCustomProvider && (
              <div className="form-group">
                <label htmlFor="customProvider">Custom Provider Name</label>
                <input
                  type="text"
                  id="customProvider"
                  name="customProvider"
                  value={formData.customProvider}
                  onChange={handleInputChange}
                  placeholder="e.g., My Company Mail"
                />
              </div>
            )}
            <div className="server-settings-grid">
              <div className="form-group">
                <label htmlFor="imapHost">IMAP Host *</label>
                <input
                  type="text"
                  id="imapHost"
                  name="imapHost"
                  value={formData.imapHost}
                  onChange={handleInputChange}
                  className={errorMessage && !formData.imapHost.trim() ? "error" : ""}
                  disabled={!isCustomProvider}
                />
                {errorMessage && !formData.imapHost.trim() && (
                  <span className="error-message">IMAP Host is required</span>
                )}
              </div>
              <div className="form-group">
                <label htmlFor="imapPort">IMAP Port *</label>
                <div className="port-input-container">
                  <input
                    type="text"
                    id="imapPort"
                    name="imapPort"
                    value={formData.imapPort}
                    onChange={handleInputChange}
                    className={errorMessage && !formData.imapPort.trim() ? "error" : ""}
                    disabled={!isCustomProvider}
                  />
                  {isCustomProvider && (
                    <div className="quick-ports">
                      <button
                        type="button"
                        onClick={() => quickFillPort("imapPort", "993")}
                      >
                        993
                      </button>
                      <button
                        type="button"
                        onClick={() => quickFillPort("imapPort", "143")}
                      >
                        143
                      </button>
                    </div>
                  )}
                </div>
                {errorMessage && !formData.imapPort.trim() && (
                  <span className="error-message">IMAP Port is required</span>
                )}
              </div>
              <div className="form-group">
                <label htmlFor="smtpHost">SMTP Host *</label>
                <input
                  type="text"
                  id="smtpHost"
                  name="smtpHost"
                  value={formData.smtpHost}
                  onChange={handleInputChange}
                  className={errorMessage && !formData.smtpHost.trim() ? "error" : ""}
                  disabled={!isCustomProvider}
                />
                {errorMessage && !formData.smtpHost.trim() && (
                  <span className="error-message">SMTP Host is required</span>
                )}
              </div>
              <div className="form-group">
                <label htmlFor="smtpPort">SMTP Port *</label>
                <div className="port-input-container">
                  <input
                    type="text"
                    id="smtpPort"
                    name="smtpPort"
                    value={formData.smtpPort}
                    onChange={handleInputChange}
                    className={errorMessage && !formData.smtpPort.trim() ? "error" : ""}
                    disabled={!isCustomProvider}
                  />
                  {isCustomProvider && (
                    <div className="quick-ports">
                      <button
                        type="button"
                        onClick={() => quickFillPort("smtpPort", "587")}
                      >
                        587
                      </button>
                      <button
                        type="button"
                        onClick={() => quickFillPort("smtpPort", "465")}
                      >
                        465
                      </button>
                      <button
                        type="button"
                        onClick={() => quickFillPort("smtpPort", "25")}
                      >
                        25
                      </button>
                    </div>
                  )}
                </div>
                {errorMessage && !formData.smtpPort.trim() && (
                  <span className="error-message">SMTP Port is required</span>
                )}
              </div>
            </div>
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="useSsl"
                  checked={formData.useSsl}
                  onChange={handleInputChange}
                />
                <span>Use SSL/TLS</span>
              </label>
              <p className="help-text">Recommended for secure connections</p>
            </div>

            {/* Help Section */}
            <div className="help-section" style={{ marginTop: "20px" }}>
              <button
                type="button"
                className="help-toggle"
                onClick={() => setShowHelp(!showHelp)}
                style={{
                  background: "none",
                  border: "none",
                  color: "#0d9488",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  padding: "8px 0",
                  fontSize: "0.9rem",
                  fontWeight: 500,
                }}
              >
                {showHelp ? '▲' : '▼'} Need help with email server settings?
              </button>

              {showHelp && (
                <div
                  className="help-content"
                  style={{
                    marginTop: "15px",
                    padding: "15px",
                    backgroundColor: "#f8fafc",
                    borderRadius: "8px",
                    border: "1px solid #e2e8f0",
                  }}
                >
                  <h4
                    style={{
                      marginTop: 0,
                      marginBottom: "15px",
                      fontSize: "1rem",
                    }}
                  >
                    How to find your email server settings
                  </h4>
                  <p
                    style={{
                      marginTop: 0,
                      marginBottom: "15px",
                      lineHeight: 1.6,
                    }}
                  >
                    For custom email domains, you'll need to get these details
                    from your email provider or IT department. Here are some
                    common settings:
                  </p>

                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr",
                      gap: "20px",
                      marginBottom: "20px",
                    }}
                  >
                    <div>
                      <h5
                        style={{
                          marginTop: 0,
                          marginBottom: "10px",
                          fontSize: "0.9rem",
                        }}
                      >
                        Common IMAP Settings
                      </h5>
                      <p style={{ margin: "5px 0", fontSize: "0.85rem" }}>
                        <strong>Host:</strong> mail.yourdomain.com or
                        imap.yourdomain.com
                      </p>
                      <p style={{ margin: "5px 0", fontSize: "0.85rem" }}>
                        <strong>Port:</strong> 993 (SSL) or 143 (TLS)
                      </p>
                      <p style={{ margin: "5px 0", fontSize: "0.85rem" }}>
                        <strong>Security:</strong> SSL/TLS or STARTTLS
                      </p>
                    </div>

                    <div>
                      <h5
                        style={{
                          marginTop: 0,
                          marginBottom: "10px",
                          fontSize: "0.9rem",
                        }}
                      >
                        Common SMTP Settings
                      </h5>
                      <p style={{ margin: "5px 0", fontSize: "0.85rem" }}>
                        <strong>Host:</strong> mail.yourdomain.com or
                        smtp.yourdomain.com
                      </p>
                      <p style={{ margin: "5px 0", fontSize: "0.85rem" }}>
                        <strong>Port:</strong> 465 (SSL) or 587 (TLS)
                      </p>
                      <p style={{ margin: "5px 0", fontSize: "0.85rem" }}>
                        <strong>Security:</strong> SSL/TLS or STARTTLS
                      </p>
                    </div>
                  </div>

                  <div>
                    <h5
                      style={{
                        marginTop: 0,
                        marginBottom: "10px",
                        fontSize: "0.95rem",
                      }}
                    >
                      Common Providers Configuration
                    </h5>
                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns:
                          "repeat(auto-fill, minmax(200px, 1fr))",
                        gap: "15px",
                      }}
                    >
                      <div
                        style={{
                          backgroundColor: "white",
                          padding: "12px",
                          borderRadius: "6px",
                          border: "1px solid #e2e8f0",
                        }}
                      >
                        <h6
                          style={{
                            marginTop: 0,
                            marginBottom: "8px",
                            fontSize: "0.85rem",
                          }}
                        >
                          Microsoft 365/Exchange
                        </h6>
                        <p style={{ margin: "4px 0", fontSize: "0.8rem" }}>
                          IMAP: outlook.office365.com (993/SSL)
                        </p>
                        <p style={{ margin: "4px 0", fontSize: "0.8rem" }}>
                          SMTP: smtp.office365.com (587/STARTTLS)
                        </p>
                      </div>
                      <div
                        style={{
                          backgroundColor: "white",
                          padding: "12px",
                          borderRadius: "6px",
                          border: "1px solid #e2e8f0",
                        }}
                      >
                        <h6
                          style={{
                            marginTop: 0,
                            marginBottom: "8px",
                            fontSize: "0.85rem",
                          }}
                        >
                          Zoho Mail
                        </h6>
                        <p style={{ margin: "4px 0", fontSize: "0.8rem" }}>
                          IMAP: imap.zoho.com (993/SSL)
                        </p>
                        <p style={{ margin: "4px 0", fontSize: "0.8rem" }}>
                          SMTP: smtp.zoho.com (465/SSL)
                        </p>
                      </div>
                      <div
                        style={{
                          backgroundColor: "white",
                          padding: "12px",
                          borderRadius: "6px",
                          border: "1px solid #e2e8f0",
                        }}
                      >
                        <h6
                          style={{
                            marginTop: 0,
                            marginBottom: "8px",
                            fontSize: "0.85rem",
                          }}
                        >
                          Rackspace
                        </h6>
                        <p style={{ margin: "4px 0", fontSize: "0.8rem" }}>
                          IMAP: secure.emailsrvr.com (993/SSL)
                        </p>
                        <p style={{ margin: "4px 0", fontSize: "0.8rem" }}>
                          SMTP: secure.emailsrvr.com (465/SSL)
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div className="advanced-options">
              <button
                type="button"
                className="btn-link"
                onClick={() => setShowAdvanced(!showAdvanced)}
              >
                {showAdvanced ? '▲' : '▼'}
                {showAdvanced
                  ? "Hide Advanced Options"
                  : "Show Advanced Options"}
              </button>
              {showAdvanced && (
                <div className="advanced-options-content">
                  <div className="form-group">
                    <label htmlFor="notes">Notes</label>
                    <textarea
                      id="notes"
                      name="notes"
                      value={formData.notes}
                      onChange={handleInputChange}
                      placeholder="Any additional notes or instructions..."
                      rows={3}
                    />
                  </div>
                  <div className="form-group checkbox-group">
                    <label>
                      <input
                        type="checkbox"
                        name="useSecure"
                        checked={formData.useSecure}
                        onChange={handleInputChange}
                      />
                      <span>Use secure connection (STARTTLS)</span>
                    </label>
                  </div>
                </div>
              )}
            </div>
          </div>
        );
      case 3:
        return (
          <div className="form-step">
            <h3>Attachments</h3>
            <p className="form-instruction">
              Upload any files you'd like to attach to your email. (Optional)
            </p>
            <div
              className={`file-upload-container ${
                fileNames.length > 0 ? "has-files" : ""
              }`}
            >
              <div className="file-upload-box">
                <p>Drag & drop files here or click to browse</p>
                <input
                  type="file"
                  id="file-upload"
                  onChange={handleFileChange}
                  multiple
                  accept=".pdf,.doc,.docx,.txt,.xls,.xlsx,.csv,.jpg,.jpeg,.png"
                  className="file-input"
                  aria-label="Upload files"
                />
                <label htmlFor="file-upload" className="btn btn-outline">
                  Select Files
                </label>
              </div>
              {fileNames.length > 0 && (
                <div className="file-list">
                  <h4>Selected Files:</h4>
                  <ul>
                    {fileNames.map((fileName, index) => (
                      <li key={index}>
                        <span>{fileName}</span>
                        <button
                          type="button"
                          className="btn-link btn-remove"
                          onClick={() => removeFile(index)}
                          aria-label={`Remove ${fileName}`}
                        >
                          ×
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* PDF Instructions Section */}
              <div className="pdf-instructions">
                <h4>PDF Requirements</h4>
                <p>Please ensure that the PDF includes the following sections in order:</p>
                <ol>
                  <li>
                    <strong>Company Name</strong>
                    <p className="indent">The official name of the company or organization.</p>
                  </li>
                  <li>
                    <strong>Description</strong>
                    <p className="indent">A short and clear summary of what the company does.</p>
                    <p className="indent">This should include the industry, mission, and any special focus areas.</p>
                  </li>
                  <li>
                    <strong>Products and Demo</strong>
                    <p className="indent">A list or brief description of all products or services offered.</p>
                    <p className="indent">Mention if a product demo is available (and how to access it – link, video, trial, etc.).</p>
                  </li>
                  <li>
                    <strong>Customer Problems and Solutions</strong>
                    <p className="indent">What common problems or challenges your customers face.</p>
                    <p className="indent">How your company's products/services solve those problems.</p>
                  </li>
                  <li>
                    <strong>Key Offerings</strong>
                    <p className="indent">Highlight the most valuable features, services, or packages your company provides.</p>
                    <p className="indent">Think of this as the top benefits or selling points.</p>
                  </li>
                  <li>
                    <strong>Website Link</strong>
                    <p className="indent">Include the official website URL for users to visit for more information.</p>
                  </li>
                </ol>
                <div className="logo-note">
                  <strong>Note:</strong> Please include your company logo in JPG format if available.
                </div>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  const isLastStep = currentStep === totalSteps;
  const isFirstStep = currentStep === 1;

  // Add axios response interceptor to handle 403 errors globally
  useEffect(() => {
    // We don't need to add another interceptor here since we already have one at the top of the file
    // that handles 403 errors. The interceptor at the top will handle all API errors consistently.
    
    // If you need to handle 403 errors differently in this component,
    // you can add specific logic in the error handling of your API calls.
  }, []);

  // Wrap the form content in a form element
  return (
    <form className="email-config-form" onSubmit={(e) => e.preventDefault()}>
      <div className="form-container">
        <div className="form-header">
          <h2>Email Configuration</h2>
          <p className="form-subtitle">
            Configure your email settings to get started
          </p>
          <div className="progress-steps">
            {[1, 2, 3].map((step) => (
              <div
                key={step}
                className={`step ${currentStep === step ? "active" : ""} ${
                  currentStep > step ? "completed" : ""
                }`}
                onClick={() => setCurrentStep(step)}
              >
                <div className="step-number">{step}</div>
                <div className="step-label">
                  {step === 1 && "Account"}
                  {step === 2 && "Server"}
                  {step === 3 && "Attachments"}
                </div>
              </div>
            ))}
          </div>
        </div>
        {errorMessage && (
          <div className="alert alert-error" style={{ marginBottom: '20px' }}>
            {errorMessage}
          </div>
        )}

        {/* Only wrap the final submit in a form */}
        <div className="form-content">
          {renderStepContent()}

          <div className="form-actions">
            {!isFirstStep && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={prevStep}
              >
                &larr; Back
              </button>
            )}

            {!isLastStep ? (
              <button
                type="button"
                className="btn btn-primary"
                onClick={nextStep}
              >
                Next &rarr;
              </button>
            ) : (
              <button
                type="button"
                className={`btn btn-primary ${isSubmitting ? 'btn-loading' : ''}`}
                onClick={handleSubmit}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <span className="spinner"></span>
                    Submitting...
                  </>
                ) : (
                  'Submit Configuration'
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </form>
  );
}

export default EmailMainForm;
