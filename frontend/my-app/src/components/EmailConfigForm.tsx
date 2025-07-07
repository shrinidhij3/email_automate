import React, { useState, useRef, useEffect } from "react";
import type { FormEvent, ChangeEvent } from "react";
import axios from "axios";
import "./EmailConfigForm.css";

// Import API configuration
import { API_BASE_URL, ENDPOINTS } from "../config/api";

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
  const [showHelp, setShowHelp] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isMounted = useRef(true);

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
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Log form submission attempt
      console.log("Form submitted with data:", {
        ...formData,
        password: formData.password ? "***" : "not provided",
      });

      // Get CSRF token from cookies or fetch a new one
      let currentCsrfToken = document.cookie.match(/\bcsrftoken=([^;]+)/)?.[1];

      if (!currentCsrfToken) {
        try {
          const csrfUrl = ENDPOINTS.AUTH.CSRF;
          const csrfResponse = await axios.get(csrfUrl, {
            withCredentials: true,
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
          });

          currentCsrfToken =
            csrfResponse.data?.csrfToken || csrfResponse.data?.csrf;
        } catch (csrfError) {
          console.warn(
            "CSRF token fetch failed (continuing anyway):",
            csrfError
          );
        }
      }

      // Prepare form data
      const formDataToSend = new FormData();
      formDataToSend.append("name", formData.name);
      formDataToSend.append("email", formData.email);
      formDataToSend.append("password", formData.password);

      const providerValue =
        formData.provider === "other" && formData.customProvider
          ? formData.customProvider
          : formData.provider;
      formDataToSend.append("provider", providerValue);

      formDataToSend.append("imap_host", formData.imapHost);
      formDataToSend.append("imap_port", formData.imapPort);
      formDataToSend.append("smtp_host", formData.smtpHost);
      formDataToSend.append("smtp_port", formData.smtpPort);
      formDataToSend.append("secure", formData.useSecure.toString());
      formDataToSend.append("use_ssl", formData.useSsl.toString());
      formDataToSend.append("notes", formData.notes || "");

      // Try to submit the form (but don't fail if it doesn't work)
      let submissionId = null;
      try {
        // Use the correct API endpoint with /api/ prefix
        const endpoint = `${API_BASE_URL}api/unread-emails/`;
        console.log("Attempting to submit to:", endpoint);

        const config = {
          headers: {
            "Content-Type": "multipart/form-data",
            ...(currentCsrfToken && { "X-CSRFToken": currentCsrfToken }),
            "X-Requested-With": "XMLHttpRequest",
            Accept: "application/json",
          },
          withCredentials: true,
          timeout: 30000,
          xsrfCookieName: "csrftoken",
          xsrfHeaderName: "X-CSRFToken",
          validateStatus: (status: number) => status < 500, // Accept any status code below 500
        };

        const response = await axios.post(endpoint, formDataToSend, config);
        console.log(
          "Form submission response:",
          response.status,
          response.data
        );

        if (response.data?.id) {
          submissionId = response.data.id;
        }
      } catch (submitError) {
        console.log(
          "Form submission failed (continuing to show thank you):",
          submitError
        );
      }

      // Try to upload files in background if we have a submission ID
      if (formData.files && formData.files.length > 0 && submissionId) {
        const fileUploadPromises = Array.from(formData.files).map(
          async (file) => {
            try {
              const fileFormData = new FormData();
              // Use 'file' as the field name to match backend expectations
              fileFormData.append("file", file);

              // Use the correct campaign upload endpoint
              const uploadUrl = new URL(
                ENDPOINTS.CAMPAIGNS.UPLOAD_ATTACHMENTS(submissionId.toString()),
                API_BASE_URL
              ).toString();

              await axios.post(uploadUrl, fileFormData, {
                headers: {
                  "Content-Type": "multipart/form-data",
                  ...(currentCsrfToken && { "X-CSRFToken": currentCsrfToken }),
                  "X-Requested-With": "XMLHttpRequest",
                },
                withCredentials: true,
                timeout: 120000, // Increased to 2 minutes (120,000ms)
                validateStatus: (status) => status < 500,
              });

              console.log(`File upload attempted for ${file.name}`);
            } catch (uploadError) {
              console.log(`File upload failed for ${file.name}:`, uploadError);
            }
          }
        );

        // Don't wait for file uploads - let them happen in background
        Promise.allSettled(fileUploadPromises)
          .then((results) => console.log("File upload results:", results))
          .catch((err) => console.log("File upload error:", err));
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

  // Toggle help section
  const toggleHelp = () => setShowHelp(!showHelp);

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
              </div>

              {/* Help Section */}
              <div className="help-section">
                <button
                  type="button"
                  className="help-toggle"
                  onClick={toggleHelp}
                  aria-expanded={showHelp}
                >
                  Need help with email server settings?
                </button>

                {showHelp && (
                  <div className="help-content">
                    <h4>How to find your email server settings</h4>
                    <p>
                      For custom email domains, you'll need to get these details
                      from your email provider or IT department. Here are some
                      common settings:
                    </p>

                    <div className="server-examples">
                      <div className="server-example">
                        <h5>Common IMAP Settings</h5>
                        <p>
                          <strong>Host:</strong> mail.yourdomain.com or
                          imap.yourdomain.com
                        </p>
                        <p>
                          <strong>Port:</strong> 993 (SSL) or 143 (TLS)
                        </p>
                        <p>
                          <strong>Security:</strong> SSL/TLS or STARTTLS
                        </p>
                      </div>

                      <div className="server-example">
                        <h5>Common SMTP Settings</h5>
                        <p>
                          <strong>Host:</strong> mail.yourdomain.com or
                          smtp.yourdomain.com
                        </p>
                        <p>
                          <strong>Port:</strong> 465 (SSL) or 587 (TLS)
                        </p>
                        <p>
                          <strong>Security:</strong> SSL/TLS or STARTTLS
                        </p>
                      </div>
                    </div>

                    <div className="common-providers">
                      <h5>Common Providers Configuration</h5>
                      <div className="provider-grid">
                        <div className="provider-card">
                          <h6>Microsoft 365/Exchange</h6>
                          <p>IMAP: outlook.office365.com (993/SSL)</p>
                          <p>SMTP: smtp.office365.com (587/STARTTLS)</p>
                        </div>
                        <div className="provider-card">
                          <h6>Zoho Mail</h6>
                          <p>IMAP: imap.zoho.com (993/SSL)</p>
                          <p>SMTP: smtp.zoho.com (465/SSL)</p>
                        </div>
                        <div className="provider-card">
                          <h6>Rackspace</h6>
                          <p>IMAP: secure.emailsrvr.com (993/SSL)</p>
                          <p>SMTP: secure.emailsrvr.com (465/SSL)</p>
                        </div>
                        <div className="provider-card">
                          <h6>Yahoo Mail</h6>
                          <p>IMAP: imap.mail.yahoo.com (993/SSL)</p>
                          <p>SMTP: smtp.mail.yahoo.com (587/STARTTLS)</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
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
              <h3>Attachments (Optional)</h3>
              <div className="form-group">
                <input
                  type="file"
                  id="files"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  multiple
                  style={{ display: "none" }}
                />
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleFileUploadClick}
                >
                  Choose Files
                </button>
                {formData.files && formData.files.length > 0 && (
                  <div className="file-list">
                    <p>Selected files:</p>
                    <ul>
                      {Array.from(formData.files).map((file, index) => (
                        <li key={`${file.name}-${file.size}-${index}`}>
                          {file.name} ({(file.size / 1024).toFixed(2)} KB)
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>

            {/* Configuration Help Section */}
            <div className="config-help-section">
              <button
                type="button"
                className="help-toggle"
                onClick={() => setShowHelp(!showHelp)}
                aria-expanded={showHelp}
              >
                {showHelp
                  ? "Hide Configuration Help"
                  : "Need Help? Click here for configuration instructions"}
                <span className={`arrow ${showHelp ? "up" : "down"}`}>▼</span>
              </button>

              {showHelp && (
                <div className="help-content">
                  <h3>Required Information from Your Provider</h3>
                  <p>
                    Before configuring your email client, you'll need to obtain
                    the following details from your email hosting provider:
                  </p>

                  <div className="help-columns">
                    <div className="help-column">
                      <h4>IMAP Settings:</h4>
                      <ul>
                        <li>
                          <strong>IMAP Server/Host:</strong> Usually formatted
                          as imap.yourdomain.com or imap.yourprovider.com
                        </li>
                        <li>
                          <strong>IMAP Port:</strong> Typically 993 for SSL/TLS
                          connections
                        </li>
                        <li>
                          <strong>Security:</strong> SSL or TLS encryption
                        </li>
                        <li>
                          <strong>Username:</strong> Your full email address
                          (e.g., you@yourdomain.com)
                        </li>
                        <li>
                          <strong>Password:</strong> Your email account password
                        </li>
                      </ul>
                    </div>

                    <div className="help-column">
                      <h4>SMTP Settings:</h4>
                      <ul>
                        <li>
                          <strong>SMTP Server/Host:</strong> Usually formatted
                          as smtp.yourdomain.com or smtp.yourprovider.com
                        </li>
                        <li>
                          <strong>SMTP Port:</strong> 465 for SSL or 587 for
                          TLS/STARTTLS
                        </li>
                        <li>
                          <strong>Security:</strong> SSL or TLS encryption
                        </li>
                        <li>
                          <strong>Authentication:</strong> Required (use same
                          username and password as IMAP)
                        </li>
                      </ul>
                    </div>
                  </div>

                  <div className="help-tips">
                    <h4>Tips:</h4>
                    <ul>
                      <li>
                        For Gmail, enable "Less secure app access" or use an App
                        Password if 2FA is enabled
                      </li>
                      <li>
                        For Office 365, your username is typically your full
                        email address
                      </li>
                      <li>
                        If using a custom domain, check with your hosting
                        provider for specific settings
                      </li>
                    </ul>
                  </div>
                </div>
              )}
            </div>

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
          </form>
        </div>
      </div>
    </div>
  );
};

export default EmailConfigForm;
