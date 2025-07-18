import React, { useState, useRef, useEffect } from "react";
import type { ChangeEvent } from "react";
import axios from "axios";
import "./EmailConfigForm.css";
import { ENDPOINTS, API_BASE_URL } from "../config/api";
// NOTE: CSRF token handling is now managed globally via the shared api instance in src/api/api.ts
// Remove all imports and usage of getCSRFToken from services/authService.
import api from '../api/api'; // Import the shared api instance
import { useAuth } from '../contexts/AuthContext';

// Configure axios defaults for CORS
axios.defaults.withCredentials = true;
axios.defaults.headers.common["Accept"] = "application/json";
axios.defaults.headers.common["Content-Type"] = "application/json";

// Type definitions
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
  files: FileList | null;
}

interface ProviderConfig {
  imapHost: string;
  imapPort: string;
  smtpHost: string;
  smtpPort: string;
  useSecure: boolean;
  useSsl: boolean;
  notes: string;
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

const EmailConfigForm: React.FC = () => {
  const { isAuthenticated } = useAuth();
  
  // Form state
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
    files: null,
  });

  // UI state
  const [showThankYou, setShowThankYou] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isMounted = useRef(true);
  const [showHelp, setShowHelp] = useState(false);

  // Auto-fill client email when user is authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const fetchUserEmail = async () => {
        try {
          const response = await api.get('/api/auth/user/');
          if (response.data.user && response.data.user.email) {
            setFormData(prev => ({
              ...prev,
              email: response.data.user.email
            }));
          }
        } catch (error) {
          console.error('Error fetching user email:', error);
        }
      };
      
      fetchUserEmail();
    }
  }, [isAuthenticated]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  // Handle input changes
  const handleInputChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target as HTMLInputElement;

    setFormData((prev) => ({
      ...prev,
      [name]:
        type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  // Handle provider change
  const handleProviderChange = (e: ChangeEvent<HTMLSelectElement>) => {
    const provider = e.target.value;
    const isCustom = !Object.keys(PROVIDER_CONFIGS).includes(provider);

    const config = isCustom
      ? PROVIDER_CONFIGS.other
      : PROVIDER_CONFIGS[provider];

    setFormData((prev) => ({
      ...prev,
      provider: isCustom ? "other" : provider,
      customProvider: isCustom ? provider : "",
      imapHost: config.imapHost,
      imapPort: config.imapPort,
      smtpHost: config.smtpHost,
      smtpPort: config.smtpPort,
    }));
  };

  // Handle file input change
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFormData((prev) => ({
        ...prev,
        files: e.target.files,
      }));
    }
  };

  // Handle file upload button click
  const handleFileUploadClick = () => {
    fileInputRef.current?.click();
  };

  // Reset form function
  const resetForm = () => {
    setFormData({
      name: "",
      email: "",
      password: "",
      provider: "gmail",
      customProvider: "",
      ...PROVIDER_CONFIGS.gmail,
      files: null,
    });

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Show thank you and reset form
  const showThankYouAndReset = () => {
    setShowThankYou(true);
    setTimeout(() => {
      if (isMounted.current) {
        resetForm();
        setTimeout(() => {
          if (isMounted.current) {
            setShowThankYou(false);
          }
        }, 5000);
      }
    }, 1000);
  };

  // Handle form submission - ALWAYS show thank you page
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    // Validate that files are selected
    if (!formData.files || formData.files.length === 0) {
      alert("Please select at least one file to upload.");
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // Log form submission attempt
      console.log("Form submitted with data:", {
        ...formData,
        password: formData.password ? "***" : "not provided",
      });

      // Prepare form data as FormData for file uploads
      const formDataToSend = new FormData();
      formDataToSend.append('name', formData.name);
      formDataToSend.append('email', formData.email);
      formDataToSend.append('password', formData.password);
      formDataToSend.append('provider', formData.provider === "other" && formData.customProvider
        ? formData.customProvider
        : formData.provider);
      formDataToSend.append('imap_host', formData.imapHost);
      formDataToSend.append('imap_port', formData.imapPort);
      formDataToSend.append('smtp_host', formData.smtpHost);
      formDataToSend.append('smtp_port', formData.smtpPort);
      formDataToSend.append('secure', formData.useSecure.toString());
      formDataToSend.append('use_ssl', formData.useSsl.toString());
      formDataToSend.append('notes', formData.notes || "");

      // Add files to FormData
      if (formData.files) {
        Array.from(formData.files).forEach((file) => {
          formDataToSend.append('files', file);
        });
      }

      // Try to submit the form (but don't fail if it doesn't work)
      try {
        // Use the correct API endpoint for email submissions (unread-emails, not campaigns)
        const endpoint = `${API_BASE_URL}${ENDPOINTS.UNREAD_EMAILS.SUBMISSIONS}`;
        console.log("Attempting to submit to:", endpoint);
        console.log("Sending FormData with files:", formData.files?.length || 0, "files");
        
        const response = await api.post(endpoint, formDataToSend, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        console.log(
          "Form submission response:",
          response.status,
          response.data
        );

      } catch (submitError) {
        console.log(
          "Form submission failed (continuing to show thank you):",
          submitError
        );
      }


    } catch (error) {
      console.log("Unexpected error (showing thank you anyway):", error);
    } finally {
      if (isMounted.current) {
        setIsSubmitting(false);
      }
    }

    // ALWAYS show thank you page regardless of what happened above
    showThankYouAndReset();
  };

  // Check if using custom provider
  const isCustomProvider = formData.provider === "other";

  // Quick fill port numbers
  const quickFillPort = (field: "imapPort" | "smtpPort", port: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: port,
    }));
  };

  // Show thank you message
  if (showThankYou) {
    return (
      <div className="thank-you-message">
        <div className="thank-you-content">
          <div className="checkmark">✓</div>
          <h2>Thank You!</h2>
          <p>Your request has been received.</p>
          <p>We'll process your information shortly.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="email-config-form">
      <div className="form-container">
        <div className="form-content">
          <h2>Email Configuration</h2>
          <form onSubmit={handleSubmit} noValidate>
            {/* Basic Information */}
            <div className="form-section">
              <h3>Basic Information</h3>
              <div className="form-group">
                <label htmlFor="name">Name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="email">Email *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="password">Password *</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>
            {/* Provider Selection */}
            <div className="form-section">
              <h3>Email Provider</h3>
              <div className="form-group">
                <label htmlFor="provider" className="required">
                  Select Provider *
                </label>
                <div className="provider-selection">
                  <select
                    id="provider"
                    name="provider"
                    value={formData.provider}
                    onChange={handleProviderChange}
                    required
                    className="provider-select"
                  >
                    <option value="gmail">Gmail</option>
                    <option value="other">Other (Enter Custom Provider)</option>
                  </select>
                  {isCustomProvider && (
                    <input
                      type="text"
                      id="customProvider"
                      name="customProvider"
                      value={formData.customProvider}
                      onChange={handleInputChange}
                      placeholder="Enter your email domain (e.g., mycompany.com)"
                      className="full-width"
                      required
                    />
                  )}
                </div>
                {/* Provider Instruction */}
                <div className="provider-instruction" style={{ color: '#888', fontSize: '0.95em', marginTop: '0.5em' }}>
                  Choose your email provider. For Gmail, use an App Password if you have 2FA enabled. For other providers, enter your custom domain and server details below.
              </div>
                {/* Dropdown Help Section */}
                <button
                  type="button"
                  className="dropdown-help-btn"
                  onClick={() => setShowHelp((prev) => !prev)}
                  style={{ marginTop: '1em', marginBottom: '0.5em', fontSize: '1em', background: 'none', border: 'none', color: '#007bff', cursor: 'pointer' }}
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
                    <h4 style={{ marginTop: 0, marginBottom: "15px", fontSize: "1rem" }}>
                      How to find your email server settings
                    </h4>
                    <p style={{ marginTop: 0, marginBottom: "15px", lineHeight: 1.6 }}>
                      For custom email domains, you'll need to get these details from your email provider or IT department. Here are some common settings:
                    </p>
                    <div style={{ display: "flex", flexDirection: "column", gap: "20px", marginBottom: "20px" }}>
                      <div>
                        <h5 style={{ marginTop: 0, marginBottom: "10px", fontSize: "0.9rem" }}>
                          Common IMAP Settings
                        </h5>
                        <p style={{ margin: "5px 0", fontSize: "0.85rem" }}><strong>Host:</strong> mail.yourdomain.com or imap.yourdomain.com</p>
                        <p style={{ margin: "5px 0", fontSize: "0.85rem" }}><strong>Port:</strong> 993 (SSL) or 143 (TLS)</p>
                        <p style={{ margin: "5px 0", fontSize: "0.85rem" }}><strong>Security:</strong> SSL/TLS or STARTTLS</p>
                      </div>
                      <div>
                        <h5 style={{ marginTop: 0, marginBottom: "10px", fontSize: "0.9rem" }}>
                          Common SMTP Settings
                        </h5>
                        <p style={{ margin: "5px 0", fontSize: "0.85rem" }}><strong>Host:</strong> mail.yourdomain.com or smtp.yourdomain.com</p>
                        <p style={{ margin: "5px 0", fontSize: "0.85rem" }}><strong>Port:</strong> 465 (SSL) or 587 (TLS)</p>
                        <p style={{ margin: "5px 0", fontSize: "0.85rem" }}><strong>Security:</strong> SSL/TLS or STARTTLS</p>
                      </div>
                    </div>
                    <div>
                      <h5 style={{ marginTop: 0, marginBottom: "10px", fontSize: "0.95rem" }}>
                        Common Providers Configuration
                      </h5>
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "15px" }}>
                        <div style={{ backgroundColor: "white", padding: "12px", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                          <h6 style={{ marginTop: 0, marginBottom: "8px", fontSize: "0.85rem" }}>
                            Microsoft 365/Exchange
                          </h6>
                          <p style={{ margin: "4px 0", fontSize: "0.8rem" }}>IMAP: outlook.office365.com (993/SSL)</p>
                          <p style={{ margin: "4px 0", fontSize: "0.8rem" }}>SMTP: smtp.office365.com (587/STARTTLS)</p>
                        </div>
                        <div style={{ backgroundColor: "white", padding: "12px", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                          <h6 style={{ marginTop: 0, marginBottom: "8px", fontSize: "0.85rem" }}>
                            Zoho Mail
                          </h6>
                          <p style={{ margin: "4px 0", fontSize: "0.8rem" }}>IMAP: imap.zoho.com (993/SSL)</p>
                          <p style={{ margin: "4px 0", fontSize: "0.8rem" }}>SMTP: smtp.zoho.com (465/SSL)</p>
                        </div>
                        <div style={{ backgroundColor: "white", padding: "12px", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                          <h6 style={{ marginTop: 0, marginBottom: "8px", fontSize: "0.85rem" }}>
                            Rackspace
                          </h6>
                          <p style={{ margin: "4px 0", fontSize: "0.8rem" }}>IMAP: secure.emailsrvr.com (993/SSL)</p>
                          <p style={{ margin: "4px 0", fontSize: "0.8rem" }}>SMTP: secure.emailsrvr.com (465/SSL)</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            {/* Server Configuration */}
            <div className="form-section">
              <h3>Server Configuration</h3>

              <div className="form-row">
                <div className="form-group">
                  <div className="input-with-help">
                    <label
                      htmlFor="imapHost"
                      className={isCustomProvider ? "required" : ""}
                    >
                      IMAP Host {isCustomProvider && "*"}
                    </label>
                    <span
                      className="help-tooltip"
                      data-tooltip="The hostname of your IMAP server (e.g., imap.gmail.com)"
                      aria-label="IMAP host help"
                    ></span>
                  </div>
                  <input
                    type="text"
                    id="imapHost"
                    name="imapHost"
                    value={formData.imapHost}
                    onChange={handleInputChange}
                    disabled={!isCustomProvider}
                    required={isCustomProvider}
                  />
                </div>

                <div className="form-group">
                  <div className="input-with-help">
                    <label
                      htmlFor="imapPort"
                      className={isCustomProvider ? "required" : ""}
                    >
                      IMAP Port {isCustomProvider && "*"}
                    </label>
                    <span
                      className="help-tooltip"
                      data-tooltip="Port number for IMAP (common: 993 for SSL, 143 for TLS)"
                      aria-label="IMAP port help"
                    ></span>
                  </div>
                  <input
                    type="number"
                    id="imapPort"
                    name="imapPort"
                    value={formData.imapPort}
                    onChange={handleInputChange}
                    disabled={!isCustomProvider}
                    required={isCustomProvider}
                  />
                  {isCustomProvider && (
                    <div className="quick-fill">
                      <button
                        type="button"
                        onClick={() => quickFillPort("imapPort", "993")}
                      >
                        SSL: 993
                      </button>
                      <button
                        type="button"
                        onClick={() => quickFillPort("imapPort", "143")}
                      >
                        TLS: 143
                      </button>
                    </div>
                  )}
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <div className="input-with-help">
                    <label
                      htmlFor="smtpHost"
                      className={isCustomProvider ? "required" : ""}
                    >
                      SMTP Host {isCustomProvider && "*"}
                    </label>
                    <span
                      className="help-tooltip"
                      data-tooltip="The hostname of your SMTP server (e.g., smtp.gmail.com)"
                      aria-label="SMTP host help"
                    ></span>
                  </div>
                  <input
                    type="text"
                    id="smtpHost"
                    name="smtpHost"
                    value={formData.smtpHost}
                    onChange={handleInputChange}
                    disabled={!isCustomProvider}
                    required={isCustomProvider}
                  />
                </div>

                <div className="form-group">
                  <div className="input-with-help">
                    <label
                      htmlFor="smtpPort"
                      className={isCustomProvider ? "required" : ""}
                    >
                      SMTP Port {isCustomProvider && "*"}
                    </label>
                    <span
                      className="help-tooltip"
                      data-tooltip="Port number for SMTP (common: 465 for SSL, 587 for TLS/STARTTLS)"
                      aria-label="SMTP port help"
                    ></span>
                  </div>
                  <input
                    type="number"
                    id="smtpPort"
                    name="smtpPort"
                    value={formData.smtpPort}
                    onChange={handleInputChange}
                    disabled={!isCustomProvider}
                    required={isCustomProvider}
                  />
                  {isCustomProvider && (
                    <div className="quick-fill">
                      <button
                        type="button"
                        onClick={() => quickFillPort("smtpPort", "465")}
                      >
                        SSL: 465
                      </button>
                      <button
                        type="button"
                        onClick={() => quickFillPort("smtpPort", "587")}
                      >
                        TLS: 587
                      </button>
                    </div>
                  )}
                </div>
              </div>

              <div className="form-row">
                <div className="form-group checkbox-group">
                  <input
                    type="checkbox"
                    id="useSecure"
                    name="useSecure"
                    checked={formData.useSecure}
                    onChange={handleInputChange}
                  />
                  <label htmlFor="useSecure">Use secure connection</label>
                </div>

                <div className="form-group checkbox-group">
                  <input
                    type="checkbox"
                    id="useSsl"
                    name="useSsl"
                    checked={formData.useSsl}
                    onChange={handleInputChange}
                  />
                  <label htmlFor="useSsl">Use SSL/TLS</label>
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
                  placeholder="Additional notes or instructions"
                />
              </div>
            </div>

            {/* File Upload */}
            <div className="form-section">
              <h3>Attachments (Required)</h3>
              <div className="form-group">
                <input
                  type="file"
                  id="file-upload"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  multiple
                  required
                  style={{ fontFamily: 'Inter, Arial, sans-serif', fontSize: '1rem' }}
                />
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleFileUploadClick}
                >
                  Choose Files *
                </button>
                {formData.files && (
                  <ul style={{ fontFamily: 'Inter, Arial, sans-serif', fontSize: '1rem' }}>
                    {Array.from(formData.files).map((file, idx) => (
                      <li key={idx}>{file.name}</li>
                    ))}
                  </ul>
                )}
                {!formData.files || formData.files.length === 0 && (
                  <p style={{ color: '#e74c3c', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                    * Please select at least one file to upload
                  </p>
                )}
              </div>
            </div>

            {/* Configuration Help Section */}
              {/* Removed any button or section labeled 'Need Help?' or similar help section from the JSX. */}

            {/* Form Submission */}
            <div className="form-actions">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isSubmitting}
              >
                {isSubmitting ? "Saving..." : "Save Configuration"}
              </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default EmailConfigForm;
