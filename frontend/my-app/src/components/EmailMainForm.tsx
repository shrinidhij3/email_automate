import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import {
  FiInfo,
  FiUpload,
  FiCheckCircle,
  FiAlertCircle,
  FiChevronDown,
  FiChevronUp,
  FiChevronRight,
  FiChevronLeft,
} from "react-icons/fi";
import "./EmailMain.css";

const API_BASE_URL = "http://localhost:8000/";

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(";").shift() || null;
  return null;
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

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [fileNames, setFileNames] = useState<string[]>([]);

  const navigate = useNavigate();
  const isCustomProvider = formData.provider === "other";
  const totalSteps = 3;

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
    const newErrors: Record<string, string> = {};
    if (!formData.name.trim()) newErrors.name = "Name is required";
    if (!formData.email.trim()) newErrors.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(formData.email))
      newErrors.email = "Please enter a valid email address";
    if (!formData.password) newErrors.password = "Password is required";
    if (!formData.imapHost.trim()) newErrors.imapHost = "IMAP host is required";
    if (!formData.imapPort.trim()) newErrors.imapPort = "IMAP port is required";
    if (!formData.smtpHost.trim()) newErrors.smtpHost = "SMTP host is required";
    if (!formData.smtpPort.trim()) newErrors.smtpPort = "SMTP port is required";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); // Prevent automatic form submission
    if (!validateForm()) return;
    if (isSubmitting) return;

    setIsSubmitting(true);
    setSubmitError(null);

    // Navigate to thank you page immediately
    navigate("/email-dashboard");

    // Continue with form submission in the background
    try {
      // Create the main campaign data (without files)
      const campaignData = {
        name: formData.name.trim(),
        email: formData.email.trim(),
        password: formData.password,
        provider: isCustomProvider
          ? formData.customProvider
          : formData.provider,
        imap_host: formData.imapHost,
        imap_port: formData.imapPort ? parseInt(formData.imapPort, 10) : null,
        smtp_host: formData.smtpHost,
        smtp_port: formData.smtpPort ? parseInt(formData.smtpPort, 10) : null,
        use_ssl: formData.useSsl,
        notes: formData.notes || "",
      };

      // Submit campaign data as JSON first
      const response = await axios.post(
        `${API_BASE_URL}api/campaigns/`,
        campaignData,
        {
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          withCredentials: true,
        }
      );

      // If files exist and campaign was created successfully, upload them in the background
      if (formData.files.length > 0 && response.data?.id) {
        const attachmentsFormData = new FormData();
        formData.files.forEach((file) =>
          attachmentsFormData.append("files", file)
        );

        // Don't await this - let it happen in the background
        axios
          .post(
            `${API_BASE_URL}api/campaigns/${response.data.id}/upload_attachments/`,
            attachmentsFormData,
            {
              headers: {
                "Content-Type": "multipart/form-data",
                "X-CSRFToken": getCookie("csrftoken"),
              },
              withCredentials: true,
            }
          )
          .catch((error) => {
            console.error("Background file upload error:", error);
            // Log to error tracking service if available
          });
      }
    } catch (error: unknown) {
      console.error("Background submission error:", error);
      // Log to error tracking service if available
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
              <FiInfo className="info-icon" />
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
                className={errors.name ? "error" : ""}
              />
              {errors.name && (
                <span className="error-message">{errors.name}</span>
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
                className={errors.email ? "error" : ""}
              />
              {errors.email && (
                <span className="error-message">{errors.email}</span>
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
                className={errors.password ? "error" : ""}
              />
              {errors.password && (
                <span className="error-message">{errors.password}</span>
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
              <FiInfo className="info-icon" />
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
                  className={errors.imapHost ? "error" : ""}
                  disabled={!isCustomProvider}
                />
                {errors.imapHost && (
                  <span className="error-message">{errors.imapHost}</span>
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
                    className={errors.imapPort ? "error" : ""}
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
                {errors.imapPort && (
                  <span className="error-message">{errors.imapPort}</span>
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
                  className={errors.smtpHost ? "error" : ""}
                  disabled={!isCustomProvider}
                />
                {errors.smtpHost && (
                  <span className="error-message">{errors.smtpHost}</span>
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
                    className={errors.smtpPort ? "error" : ""}
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
                {errors.smtpPort && (
                  <span className="error-message">{errors.smtpPort}</span>
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
                {showHelp ? (
                  <FiChevronUp style={{ marginRight: "8px" }} />
                ) : (
                  <FiChevronDown style={{ marginRight: "8px" }} />
                )}
                Need help with email server settings?
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
                {showAdvanced ? <FiChevronUp /> : <FiChevronDown />}
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
              <FiInfo className="info-icon" />
              Upload any files you'd like to attach to your email. (Optional)
            </p>
            <div
              className={`file-upload-container ${
                fileNames.length > 0 ? "has-files" : ""
              }`}
            >
              <div className="file-upload-box">
                <FiUpload className="upload-icon" />
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

  return (
    <div className="email-config-form">
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
        {submitError && (
          <div className="alert alert-error">
            <FiAlertCircle className="alert-icon" />
            {submitError}
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
                <FiChevronLeft /> Back
              </button>
            )}

            {!isLastStep ? (
              <button
                type="button"
                className="btn btn-primary"
                onClick={nextStep}
              >
                Next <FiChevronRight />
              </button>
            ) : (
              <form onSubmit={handleSubmit} style={{ display: "inline" }}>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <span className="spinner"></span> Submitting...
                    </>
                  ) : (
                    <>
                      <FiCheckCircle /> Submit Configuration
                    </>
                  )}
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default EmailMainForm;
