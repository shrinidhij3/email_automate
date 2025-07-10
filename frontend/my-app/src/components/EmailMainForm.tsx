import { useState, useEffect } from "react";
import "./EmailMain.css";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import api from "../api/api";

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
  const [isUploadingFiles, setIsUploadingFiles] = useState<boolean>(false);
  const totalSteps = 3;
  
  const isCustomProvider = formData.provider === "other";
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

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
  }, [formData.provider, isCustomProvider]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
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
      setIsUploadingFiles(true);
      const newFiles = Array.from(e.target.files);
      setFormData((prev) => ({
        ...prev,
        files: [...prev.files, ...newFiles],
      }));
      setFileNames((prev) => [
        ...prev,
        ...newFiles.map((file: File) => file.name),
      ]);
      // Reset upload state after a short delay
      setTimeout(() => setIsUploadingFiles(false), 1000);
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

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('=== FORM SUBMISSION STARTED ===');
    console.log('Current step:', currentStep, 'Total steps:', totalSteps);
    console.log('Is authenticated:', isAuthenticated, 'Is loading:', isLoading);
    console.log('Is submitting:', isSubmitting);
    console.log('Form data:', formData);
    
    // Prevent submission if not on last step
    if (currentStep !== totalSteps) {
      console.log('❌ Not on last step, preventing submission');
      return;
    }
    
    // Prevent submission if already submitting
    if (isSubmitting) {
      console.log('❌ Already submitting, preventing duplicate submission');
      return;
    }
    
    // Prevent submission if not authenticated
    if (!isAuthenticated) {
      console.log('❌ Not authenticated, preventing submission');
      setErrorMessage('Please log in to submit a campaign');
      return;
    }
    
    // Prevent submission if still loading auth state
    if (isLoading) {
      console.log('❌ Still loading auth state, preventing submission');
      setErrorMessage('Please wait while we verify your authentication...');
      return;
    }
    
    // Validate form
    if (!validateForm()) {
      console.log('❌ Form validation failed');
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }
    
    console.log('✅ All checks passed, starting submission');
    setIsSubmitting(true);
    setErrorMessage('');
    
    try {
      console.log('Preparing to submit campaign data...');
      let apiResponse;
      
      if (formData.files && formData.files.length > 0) {
        console.log('📁 Submitting with files:', formData.files.length, 'files');
        // Use FormData for file uploads
        const form = new FormData();
        form.append('name', formData.name.trim());
        form.append('email', formData.email.trim());
        form.append('password', formData.password);
        form.append('provider', isCustomProvider ? formData.customProvider : formData.provider);
        form.append('imap_host', formData.imapHost);
        form.append('imap_port', formData.imapPort ? String(formData.imapPort) : '');
        form.append('smtp_host', formData.smtpHost);
        form.append('smtp_port', formData.smtpPort ? String(formData.smtpPort) : '');
        form.append('use_ssl', String(formData.useSsl));
        form.append('notes', formData.notes || '');
        
        formData.files.forEach((file, index) => {
          console.log(`📎 Appending file ${index + 1}:`, file.name, file.size, file.type);
          form.append('uploaded_files', file);
        });
        
        console.log('🚀 Submitting FormData to /api/campaigns/');
        apiResponse = await api.post('/api/campaigns/', form);
      } else {
        console.log('📄 Submitting as JSON (no files)');
        // Send as JSON if no files
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
        console.log('📋 Campaign data to submit:', campaignData);
        console.log('🚀 Submitting JSON to /api/campaigns/');
        apiResponse = await api.post('/api/campaigns/', campaignData);
      }

      console.log('✅ Response received:', {
        status: apiResponse.status,
        statusText: apiResponse.statusText,
        data: apiResponse.data
      });
      
      if (apiResponse.status >= 400) {
        const errorDetail = apiResponse.data?.detail || 
                          apiResponse.data?.message || 
                          'No error details provided';
        console.error('❌ Campaign creation failed:', errorDetail);
        throw new Error(`Failed to create campaign: ${errorDetail}`);
      }
      
      console.log("🎉 Campaign created successfully:", apiResponse.data);
      
      // Reset form and clear error message
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
      setErrorMessage(""); // Clear any error messages
      
      // Show success message briefly
      setTimeout(() => {
        setErrorMessage("Campaign created successfully!");
        setTimeout(() => setErrorMessage(""), 3000); // Clear success message after 3 seconds
      }, 100);
      
    } catch (error: unknown) {
      console.error("❌ Campaign submission error:", error);
      
      // Handle API errors
      if (error && typeof error === 'object' && 'response' in error) {
        const apiError = error as any;
        console.log('🔍 API Error details:', {
          status: apiError.response?.status,
          statusText: apiError.response?.statusText,
          data: apiError.response?.data,
          headers: apiError.response?.headers
        });
        
        if (apiError.response?.status === 401 || apiError.response?.status === 403) {
          console.log('🔐 Authentication error, redirecting to login');
          navigate('/login');
          return;
        }
        
        // Handle HTTP errors with response
        const errorMessage = apiError.response?.data?.detail || 
                           apiError.response?.data?.message || 
                           apiError.message || 
                           "Failed to create campaign";
        setErrorMessage(`Error: ${errorMessage}`);
      } else if (error instanceof Error) {
        // Something happened in setting up the request
        console.log('🌐 Network or setup error:', error.message);
        setErrorMessage(`Error: ${error.message}`);
      } else {
        console.log('❓ Unknown error type:', error);
        setErrorMessage("An unknown error occurred. Please try again.");
      }
    } finally {
      console.log('🏁 Form submission completed, setting isSubmitting to false');
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

  // Wrap the form content in a form element
  return (
    <form
      className="email-config-form"
      onSubmit={handleSubmit}
      noValidate
      onKeyDown={e => {
        // Prevent Enter from submitting the form unless on the last step and the submit button is focused
        if (
          e.key === 'Enter' &&
          !isLastStep &&
          (e.target as HTMLElement).tagName !== 'TEXTAREA'
        ) {
          e.preventDefault();
          e.stopPropagation();
          console.log('🚫 Prevented Enter key submission on step', currentStep);
        }
      }}
      onKeyPress={e => {
        // Additional safety to prevent form submission on Enter
        if (e.key === 'Enter' && !isLastStep) {
          e.preventDefault();
          e.stopPropagation();
          console.log('🚫 Prevented Enter key press submission on step', currentStep);
        }
      }}
    >
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
                type="submit"
                className={`btn btn-primary ${isSubmitting ? 'btn-loading' : ''}`}
                disabled={isSubmitting || !isAuthenticated || isLoading || currentStep !== totalSteps || isUploadingFiles}
                onClick={(e) => {
                  console.log('🔘 Submit button clicked');
                  console.log('Button state:', {
                    isSubmitting,
                    isAuthenticated,
                    isLoading,
                    currentStep,
                    totalSteps,
                    isUploadingFiles
                  });
                  
                  // Additional safety check
                  if (isSubmitting || !isAuthenticated || isLoading || currentStep !== totalSteps || isUploadingFiles) {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('🚫 Submit button disabled, preventing submission');
                    return;
                  }
                  
                  // Ensure user is on the last step and has completed all required fields
                  if (currentStep !== totalSteps) {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('🚫 Not on last step, preventing submission');
                    return;
                  }
                }}
              >
                {isSubmitting ? (
                  <>
                    <span className="spinner"></span>
                    Submitting...
                  </>
                ) : !isAuthenticated ? (
                  'Please Log In'
                ) : isLoading ? (
                  'Loading...'
                ) : isUploadingFiles ? (
                  'Uploading Files...'
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
