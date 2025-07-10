import React, { useState, useEffect, FormEvent, ChangeEvent, FC, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { ENDPOINTS, API_BASE_URL } from "../config/api";
import api from "../api/api";
import "./EmailDashboard.css";

interface FormData {
  name: string;
  email: string;
  client_email: string;
}

interface Message {
  text: string;
  type: "success" | "error" | "";
}

interface CsvEntry {
  name: string;
  email: string;
  client_email: string;
  date_of_signup?: string;
  day_one?: string | null;
  day_two?: string | null;
  day_four?: string | null;
  day_five?: string | null;
  day_seven?: string | null;
  day_nine?: string | null;
}

const EmailDashboard: FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();
  const [formData, setFormData] = useState<FormData>({
    name: "",
    email: "",
    client_email: "",
  });
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [isSubmittingSingle, setIsSubmittingSingle] = useState(false);
  const [isSubmittingBulk, setIsSubmittingBulk] = useState(false);
  const [message, setMessage] = useState<Message>({ text: "", type: "" });

  useEffect(() => {
    if (!isAuthenticated || isLoading) return;
    
    // Auto-fill client email when user is authenticated
    const fetchUserEmail = async () => {
      try {
        const response = await api.get('/api/auth/user/');
        if (response.data.user && response.data.user.email) {
          setFormData(prev => ({
            ...prev,
            client_email: response.data.user.email
          }));
        }
      } catch (error) {
        console.error('Error fetching user email:', error);
      }
    };
    
    fetchUserEmail();
    
    // Check if user has campaigns
    api.get("/api/campaigns/check_user_campaigns/")
      .then((response: any) => {
        if (response.data.has_campaigns) {
          // User has campaigns, stay on dashboard
          console.log("User has campaigns, staying on dashboard");
        } else {
          // User has no campaigns, redirect to campaign creation
          navigate("/create-campaign");
        }
      })
      .catch((error: any) => {
        console.error("Error checking campaigns:", error);
        // If error, redirect to campaign creation
        navigate("/create-campaign");
      });
  }, [isAuthenticated, isLoading, navigate]);

  const showMessage = (text: string, type: "success" | "error" | "") => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: "", type: "" }), 5000);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    const targetForm = e.currentTarget.closest("form");
    if (targetForm?.classList.contains("csv-upload-form")) {
      await handleBulkSubmit(e);
    } else {
      await handleSingleSubmit(e);
    }
  };

  const handleSingleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim() || !formData.email.trim() || !formData.client_email.trim()) {
      showMessage("Please fill in all fields", "error");
      return;
    }

    if (!/^\S+@\S+\.\S+$/.test(formData.client_email)) {
      showMessage("Please enter a valid client email", "error");
      return;
    }

    const email = formData.email.trim().toLowerCase();
    setIsSubmittingSingle(true);

    const data = {
      name: formData.name.trim(),
      email: email,
      client_email: formData.client_email.trim(),
    };

    try {
      console.log("Sending request to:", API_BASE_URL);
      console.log("Request data:", data);

      const response = await api.post(`${ENDPOINTS.EMAIL_ENTRIES}`, data);

      console.log("Response status:", response.status);
      console.log("Response data:", response.data);

      if (response.status === 409) {
        // Duplicate email
        showMessage(`The email ${email} is already registered.`, "error");
      } else if (response.status >= 200 && response.status < 300) {
        showMessage("Email submitted successfully!", "success");
        setFormData({ name: "", email: "", client_email: "" });
        // Redirect to dashboard after a short delay to show success message
        setTimeout(() => {
          navigate('/email-dashboard');
        }, 1000);
      } else {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        if (response.data) {
          errorMessage =
            response.data.error ||
            response.data.detail ||
            response.data.message ||
            Object.entries(response.data)
              .map(([key, value]) => `${key}: ${value}`)
              .filter((_, i) => i < 3) // Limit to first 3 errors
              .join("\n") ||
            JSON.stringify(response.data);
        }
        console.error("Server error:", errorMessage);
        throw new Error(errorMessage);
      }
    } catch (_error: unknown) {
      let errorMessage = "An unknown error occurred";

      if (_error instanceof Error) {
        errorMessage = _error.message;
        console.error("Error details:", {
          name: _error.name,
          message: _error.message,
          stack: _error.stack,
        });
      } else if (typeof _error === "string") {
        errorMessage = _error;
        console.error("Error:", _error);
      } else {
        console.error("Unexpected error type:", _error);
      }

      setMessage({
        text: `Error: ${errorMessage}. Please try again.`,
        type: "error" as const,
      });
    } finally {
      setIsSubmittingSingle(false);
    }
  };

  const processCsv = (text: string): CsvEntry[] => {
    const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
    
    if (lines.length < 2) {
      throw new Error("CSV must contain at least a header row and one data row");
    }

    const headerLine = lines[0];
    const headers = headerLine.split(',').map(h => h.trim().toLowerCase());

    const requiredColumns = ['name', 'email', 'client_email'];
    const missingColumns = requiredColumns.filter(col => !headers.includes(col));

    if (missingColumns.length > 0) {
      throw new Error(`CSV must contain all required columns: ${requiredColumns.join(", ")}. Missing: ${missingColumns.join(", ")}`);
    }

    return lines
      .slice(1)
      .filter((line) => line.trim() !== "")
      .map((line, index) => {
        // Simple CSV parsing that handles quoted values
        const values = line.match(/\s*\"([^\"]*?)\"\s*,?|([^,]+),?|,/g) || [];
        const cleanValues = values.map((value) => {
          if (value === null || value === undefined) return "";
          // Remove surrounding quotes and trim
          return value.replace(/^\s*"?|\s*"?\s*,?\s*$/g, "").trim();
        });

        // Get values by header index
        const name = cleanValues[headers.indexOf("name")] || "";
        const email = cleanValues[headers.indexOf("email")]?.toLowerCase() || "";
        const client_email = cleanValues[headers.indexOf("client_email")]?.toLowerCase() || "";

        // Skip rows where all required fields are empty
        if (!name && !email && !client_email) {
          return null; // This row will be filtered out
        }

        // Validate required fields
        if (!name || !email || !client_email) {
          throw new Error(`Missing required field in row ${index + 2}. All fields (name, email, client_email) are required.`);
        }

        // Basic email validation
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
          throw new Error(`Invalid email format in row ${index + 2}: ${email}`);
        }

        // Validate client_email format if provided
        if (client_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(client_email)) {
          throw new Error(`Invalid client_email format in row ${index + 2}: ${client_email}`);
        }

        return {
          name: name.trim(),
          email: email.trim().toLowerCase(),
          client_email: client_email.trim().toLowerCase()
        };
      })
      .filter(entry => entry !== null) as CsvEntry[]; // Remove null entries
  };

  const handleBulkSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!csvFile) {
      showMessage("Please select a CSV file", "error");
      return;
    }
    if (!isAuthenticated && !isLoading) {
      navigate('/login');
      return;
    }
    setIsSubmittingBulk(true);

    const reader = new FileReader();

    reader.onload = async (e) => {
      try {
        const text = e.target?.result as string;
        const entries = processCsv(text);

        console.log("Sending bulk request with entries:", entries);

        // Send the processed entries directly to the API
        const response = await api.post(`${ENDPOINTS.EMAIL_ENTRIES}`, entries);

        if (response.status === 401 || response.status === 403) {
          navigate('/login');
          return;
        }

        // Handle axios response properly
        const result = response.data;

        if (
          response.status === 400 &&
          result.status === "duplicate_in_request"
        ) {
          // Duplicate emails in the same file
          const dupEmails = result.duplicate_emails || [];
          const displayDups =
            dupEmails.length > 3
              ? `${dupEmails.slice(0, 3).join(", ")} and ${
                  dupEmails.length - 3
                } more`
              : dupEmails.join(", ");

          showMessage(
            `Found ${dupEmails.length} duplicate email(s) in the file: ${displayDups}`,
            "error"
          );
        } else if (response.status === 200 || response.status === 207) {
          // Success or partial success
          const successMsg = [];

          if (result.created > 0) {
            successMsg.push(`Successfully added ${result.created} email(s)`);
          }

          if (result.duplicates > 0) {
            const dupEmails = result.duplicate_emails || [];
            const displayDups =
              dupEmails.length > 3
                ? `${dupEmails.slice(0, 3).join(", ")} and ${
                    dupEmails.length - 3
                  } more`
                : dupEmails.join(", ");

            successMsg.push(
              `Skipped ${result.duplicates} duplicate(s)` +
                (dupEmails.length ? `: ${displayDups}` : "")
            );
          }

          showMessage(successMsg.join(". "), "success");

          // Reset form if everything was successful
          if (result.created > 0 || result.duplicates === 0) {
            setCsvFile(null);
            const fileInput = document.getElementById(
              "csv-upload"
            ) as HTMLInputElement;
            if (fileInput) fileInput.value = "";
          }
        } else {
          // Handle other API errors
          let errorMessage = result.error || "Failed to process CSV";
          if (result.duplicate_emails?.length > 0) {
            errorMessage += ` (${result.duplicate_emails.length} duplicates found)`;
          }
          throw new Error(errorMessage);
        }
      } catch (error) {
        console.error("Upload error:", error);
        let errorMessage = "Error processing CSV";
        if (error instanceof Error) {
          errorMessage = error.message;
        } else if (typeof error === "string") {
          errorMessage = error;
        }
        showMessage(errorMessage, "error");
      } finally {
        setIsSubmittingBulk(false);
      }
    };

    reader.onerror = () => {
      showMessage("Error reading file", "error");
      setIsSubmittingBulk(false);
    };

    reader.readAsText(csvFile);
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    setCsvFile(file || null);
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="email-dashboard">
      <h1>Email Submission Dashboard</h1>

      {message.text && (
        <div className={`message ${message.type}`}>{message.text}</div>
      )}

      <div className="forms-container">
        <div className="form-section">
          <h2>Single Email Submission</h2>
          <form onSubmit={handleSubmit} className="single-email-form">
            <div className="form-group">
              <label htmlFor="name">Name:</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Name"
                required
                disabled={isSubmittingSingle || isSubmittingBulk}
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email:</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Email"
                required
                disabled={isSubmittingSingle || isSubmittingBulk}
              />
            </div>
            <div className="form-group">
              <label htmlFor="client_email">Client Email:</label>
              <input
                type="email"
                id="client_email"
                name="client_email"
                value={formData.client_email}
                onChange={handleInputChange}
                placeholder="Enter client's email"
                required
                disabled={isSubmittingSingle || isSubmittingBulk}
              />
            </div>
            <button
              type="submit"
              className={`submit-btn ${isSubmittingSingle ? "loading" : ""}`}
              disabled={isSubmittingSingle || isSubmittingBulk}
            >
              {isSubmittingSingle ? "Submitting..." : "Submit Email"}
            </button>
          </form>
        </div>

        <div className="form-section">
          <h2>Bulk CSV Upload</h2>
          <form onSubmit={handleSubmit} className="csv-upload-form">
            <div className="form-group">
              <label htmlFor="csv-upload">Upload CSV File:</label>
              <input
                type="file"
                id="csv-upload"
                accept=".csv,.txt,.pdf,.doc,.docx"
                onChange={handleFileChange}
                required
                disabled={isSubmittingBulk}
              />
              <small>
                Upload CSV file with required columns: 'name', 'email', and 'client_email'. 
                All fields are required in each row.
              </small>
            </div>
            <button
              type="submit"
              className={`submit-btn ${isSubmittingBulk ? "loading" : ""}`}
              disabled={!csvFile || isSubmittingBulk || isSubmittingSingle}
              title={!csvFile ? "Please select a file first" : ""}
            >
              {isSubmittingBulk ? "Uploading..." : "Upload File"}
            </button>
            {csvFile && (
              <div className="file-info">
                Selected: {csvFile.name} ({(csvFile.size / 1024).toFixed(2)} KB)
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};

export default EmailDashboard;
