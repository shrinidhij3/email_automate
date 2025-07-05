import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./Home.css";

// SVG Icons
const RocketIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M13 3a16 16 0 0 0-6 2C3 7 1 12 2 17c2 0 4-1 6-2s4-2 6-2c3 1 6 2 9 2s3-5-1-10c-2 0-4 1-6 2"></path>
    <path d="M12 15c4 0 5 2 5 2v4s-1 1-5 1-5-1-5-1v-4s1-2 5-2z"></path>
    <path d="M8 22v-5s-4-1-4-5l4-1"></path>
    <path d="M16 10l4-1s0 4-4 5v1"></path>
  </svg>
);

const AnalyticsIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M21 3v18h-6"></path>
    <path d="M9 15H3V9h6"></path>
    <path d="M21 3l-7 8-4-4-7 8"></path>
  </svg>
);

const ShieldIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
  </svg>
);

const ClockIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="12" cy="12" r="10"></circle>
    <polyline points="12 6 12 12 16 14"></polyline>
  </svg>
);

const MailIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
    <polyline points="22,6 12,13 2,6"></polyline>
  </svg>
);

const UsersIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
    <circle cx="9" cy="7" r="4"></circle>
    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
  </svg>
);

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    // Add Inter font from Google Fonts
    const link = document.createElement("link");
    link.href =
      "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap";
    link.rel = "stylesheet";
    document.head.appendChild(link);

    return () => {
      document.head.removeChild(link);
    };
  }, []);

  const handleUnreadEmailsClick = () => {
    navigate("/unread-emails");
  };

  const handleEmailCampaignClick = () => {
    if (isAuthenticated) {
      navigate("/email-dashboard");
    } else {
      navigate("/login", { state: { from: "/email-dashboard" } });
    }
  };

  return (
    <div className="home-container">
      <div className="hero">
        <h1 className="main-heading">
          <span className="highlight">Transform</span> Your Email Marketing
        </h1>
        <p className="hero-subtitle">
          Streamline your communication with our powerful email automation
          solution. Generate leads, manage campaigns, and track engagement—all
          in one place.
        </p>

        <div className="cta-buttons">
          <button
            className="btn btn-primary"
            onClick={handleUnreadEmailsClick}
            style={{
              padding: "0.75rem 1.5rem",
              fontSize: "1.1rem",
              display: "flex",
              alignItems: "center",
              backgroundColor: "#0d9488",
              border: "none",
              borderRadius: "0.5rem",
              color: "white",
              transition: "background-color 0.2s, transform 0.2s",
            }}
            onMouseOver={(e) =>
              (e.currentTarget.style.backgroundColor = "#0f766e")
            }
            onMouseOut={(e) =>
              (e.currentTarget.style.backgroundColor = "#0d9488")
            }
            onMouseDown={(e) =>
              (e.currentTarget.style.transform = "scale(0.98)")
            }
            onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "#0d9488";
              e.currentTarget.style.transform = "scale(1)";
            }}
          >
            <div style={{ marginRight: "0.5rem" }}>
              <MailIcon />
            </div>
            <span>Unread Emails</span>
          </button>
          <button
            className="btn btn-secondary"
            onClick={handleEmailCampaignClick}
            style={{
              padding: "0.75rem 1.5rem",
              fontSize: "1.1rem",
              display: "flex",
              alignItems: "center",
              backgroundColor: "white",
              border: "1px solid #0d9488",
              color: "#0d9488",
              transition: "all 0.2s",
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = "#f0fdfa";
              e.currentTarget.style.color = "#0f766e";
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = "white";
              e.currentTarget.style.color = "#0d9488";
            }}
          >
            <div style={{ marginRight: "0.5rem" }}>
              <UsersIcon />
            </div>
            <span>Email Campaign</span>
          </button>
        </div>

        <div className="features">
          <div className="feature">
            <div className="feature-icon">
              <RocketIcon />
            </div>
            <h3>Fast & Efficient</h3>
            <p>Process emails in bulk with our high-performance system</p>
          </div>
          <div className="feature">
            <div className="feature-icon">
              <AnalyticsIcon />
            </div>
            <h3>Smart Analytics</h3>
            <p>Track engagement and optimize your campaigns</p>
          </div>
          <div className="feature">
            <div className="feature-icon">
              <ShieldIcon />
            </div>
            <h3>Secure & Private</h3>
            <p>Your data is always protected and encrypted</p>
          </div>
          <div className="feature">
            <div className="feature-icon">
              <ClockIcon />
            </div>
            <h3>24/7 Support</h3>
            <p>Round-the-clock assistance for all your needs</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
