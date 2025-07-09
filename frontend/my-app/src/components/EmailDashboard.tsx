import { useState, useEffect } from "react";
import type { ChangeEvent, FormEvent, FC } from "react";
import { useNavigate } from "react-router-dom";
import "./EmailDashboard.css";
import { API_BASE_URL, ENDPOINTS } from "../config/api";

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

// API base URL is imported from config/api

// Function to get CSRF token from cookies
const getCsrfToken = (): string | null => {
  const cookieValue = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];
  return cookieValue ? decodeURIComponent(cookieValue) : null;
};

// Function to get CSRF token from the server
const fetchCsrfToken = async (): Promise<string | null> => {
  try {
    // Use the correct authentication endpoint for CSRF token
    const response = await fetch(`${API_BASE_URL}${ENDPOINTS.AUTH.CSRF}`, {
      method: "GET",
      credentials: "include",
    });

    if (response.ok) {
      const data = await response.json();
      return data.csrfToken || null;
    }
    return null;
  } catch (error) {
    console.error("Error fetching CSRF token:", error);
    return null;
  }
};

const EmailDashboard: FC = () => {
  const [formData, setFormData] = useState<FormData>({
    name: "",
    email: "",
    client_email: "",
  });
  const [csrfToken, setCsrfToken] = useState<string | null>(null);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [isSubmittingSingle, setIsSubmittingSingle] = useState(false);
  const [isSubmittingBulk, setIsSubmittingBulk] = useState(false);
  const [message, setMessage] = useState<Message>({ text: "", type: "" });
  const navigate = useNavigate();

  // Fetch CSRF token on component mount
  useEffect(() => {
    const initializeCsrfToken = async () => {
      // First try to get from cookies
      let token = getCsrfToken();

      if (!token) {
        // If not in cookies, fetch from the server
        token = await fetchCsrfToken();
      }

      if (token) {
        setCsrfToken(token);
      } else {
        console.warn("Could not retrieve CSRF token");
      }
    };

    initializeCsrfToken();

    // Set up a timer to refresh the CSRF token every 30 minutes
    const tokenRefreshInterval = setInterval(() => {
      fetchCsrfToken().then((token) => {
        if (token) {
          setCsrfToken(token);
        }
      });
    }, 30 * 60 * 1000); // 30 minutes

    return () => clearInterval(tokenRefreshInterval);
  }, []);

  // Helper function to make authenticated requests with CSRF token
  const makeRequest = async (url: string, options: RequestInit = {}) => {
    console.log("Making request to:", url);
    console.log("Request options:", {
      method: options.method,
      headers: options.headers,
      body: options.body,
    });

    // Ensure we have a CSRF token
    let token = csrfToken;
    if (!token) {
      token = await fetchCsrfToken();
      if (token) {
        setCsrfToken(token);
      }
    }

    const headers = new Headers({
      Accept: "application/json",
      ...(options.method !== "GET" && { "X-CSRFToken": token || "" }),
      ...((options.headers as Record<string, string>) || {}),
    });

    // Only set Content-Type for non-form-data requests
    if (!(options.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        credentials: "include",
        mode: "cors",
      });

      console.log("Response status:", response.status, response.statusText);
      console.log(
        "Response headers:",
        Object.fromEntries(response.headers.entries())
      );

      // Clone the response to read it for logging
      const responseClone = response.clone();
      try {
        const data = await responseClone.json();
        console.log("Response data:", data);
      } catch (e) {
        console.log("No JSON response body");
      }

      return response;
    } catch (error) {
      console.error("Request failed:", error);
      throw error;
    }
  };

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

      const response = await makeRequest(`${API_BASE_URL}${ENDPOINTS.EMAIL_ENTRIES}`, {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        credentials: "include",
      });

      console.log("Response status:", response.status);
      const responseData = await response.json().catch(() => ({}));
      console.log("Response data:", responseData);

      if (response.status === 409) {
        // Duplicate email
        showMessage(`The email ${email} is already registered.`, "error");
      } else if (response.ok) {
        showMessage("Email submitted successfully!", "success");
        setFormData({ name: "", email: "", client_email: "" });
        // Redirect to dashboard after a short delay to show success message
        setTimeout(() => {
          navigate('/email-dashboard');
        }, 1000);
      } else {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        if (responseData) {
          errorMessage =
            responseData.error ||
            responseData.detail ||
            responseData.message ||
            Object.entries(responseData)
              .map(([key, value]) => `${key}: ${value}`)
              .filter((_, i) => i < 3) // Limit to first 3 errors
              .join("\n") ||
            JSON.stringify(responseData);
        }
        console.error("Server error:", errorMessage);
        throw new Error(errorMessage);
      }
    } catch (error: unknown) {
      let errorMessage = "An unknown error occurred";

      if (error instanceof Error) {
        errorMessage = error.message;
        console.error("Error details:", {
          name: error.name,
          message: error.message,
          stack: error.stack,
        });
      } else if (typeof error === "string") {
        errorMessage = error;
        console.error("Error:", error);
      } else {
        console.error("Unexpected error type:", error);
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
    const lines = text.split(/\r?\n/);
    if (lines.length < 2) {
      throw new Error("CSV file is empty or has no data rows");
    }

    // Parse headers
    const headers = lines[0]
      .split(",")
      .map((h) => h.trim().toLowerCase().replace(/^"|"$/g, ""));

    // Validate CSV format - now requiring client_email as well
    const requiredColumns = ["name", "email", "client_email"];
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
      });
  };

  const handleBulkSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!csvFile) {
      showMessage("Please select a CSV file", "error");
      return;
    }

    setIsSubmittingBulk(true);

    const reader = new FileReader();

    reader.onload = async (e) => {
      try {
        const text = e.target?.result as string;
        const entries = processCsv(text);

        console.log("Sending bulk request with entries:", entries);

        // Get CSRF token
        const token = await fetchCsrfToken();
        if (!token) {
          throw new Error("Failed to get CSRF token");
        }

        // Create FormData for file upload
        const formData = new FormData();
        formData.append('file', csvFile);

        // Send the request with proper headers
        const response = await fetch(`${API_BASE_URL}${ENDPOINTS.EMAIL_ENTRIES}bulk/`, {
          method: 'POST',
          body: formData,
          credentials: 'include',
          headers: {
            'X-CSRFToken': token,
          },
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.message || 'Failed to upload CSV');
        }

        const result = await response.json();

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
        } else if (response.ok || response.status === 207) {
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
        showMessage(
          error instanceof Error ? error.message : "Error processing CSV",
          "error"
        );
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
