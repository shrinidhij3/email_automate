import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./LoginPage.css";

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login, register } = useAuth();

  const defaultRedirect = "/email-dashboard";
  const registerRedirect = "/dashboard/upload";
  // Remove unused checkAuth and from
  // const { login, register, checkAuth } = useAuth();

  // Remove this useEffect that checks for existing session on mount
  // useEffect(() => {
  //   let isMounted = true;
  //   const checkAuthStatus = async () => {
  //     try {
  //       const isAuth = await checkAuth();
  //       if (isMounted && isAuth) {
  //         navigate(from, { replace: true });
  //       }
  //     } catch (error) {
  //       console.error('Auth check failed:', error);
  //     }
  //   };
  //   if (!isLoading) {
  //     checkAuthStatus();
  //   }
  //   return () => {
  //     isMounted = false;
  //   };
  // }, [checkAuth, from, navigate, isLoading]);

  const validateEmail = (email: string): boolean => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const validateForm = (): boolean => {
    if (!username.trim()) {
      setError("Username is required");
      return false;
    }
    if (!password) {
      setError("Password is required");
      return false;
    }
    if (!isLogin) {
      if (!email.trim()) {
        setError("Email is required for registration");
        return false;
      }
      if (!validateEmail(email)) {
        setError("Please enter a valid email address");
        return false;
      }
      if (password.length < 8) {
        setError("Password must be at least 8 characters long");
        return false;
      }
      if (password !== confirmPassword) {
        setError("Passwords do not match");
        return false;
      }
      if (!firstName.trim()) {
        setError("First name is required");
        return false;
      }
      if (!lastName.trim()) {
        setError("Last name is required");
        return false;
      }
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('Form submission started', { isLogin, isLoading });
    
    setError("");
    if (!validateForm()) return;

    if (isLoading) {
      console.log('Already loading, preventing duplicate submission');
      return;
    }

    setIsLoading(true);
    try {
      if (isLogin) {
        console.log('Attempting login...');
        await login(username, password);
        console.log('Login successful, navigating to:', defaultRedirect);
        navigate(defaultRedirect, { replace: true });
      } else {
        console.log('Attempting registration...');
        await register({
          username: username.trim(),
          email: email.trim(),
          password,
          password2: confirmPassword,
          first_name: firstName.trim(),
          last_name: lastName.trim(),
        });
        console.log('Registration successful, waiting before navigation...');
        await new Promise((resolve) => setTimeout(resolve, 500));
        console.log('Navigating to:', registerRedirect);
        navigate(registerRedirect, { replace: true });
      }
    } catch (err: any) {
      console.error('Authentication error:', err);
      if (err.message && err.message.includes("Network Error")) {
        setError(
          "Unable to connect to the server. Please check your internet connection."
        );
      } else {
        setError(err.message || "Authentication failed. Please try again.");
      }
    } finally {
      console.log('Setting isLoading to false');
      setIsLoading(false);
    }
  };

  const handleBackClick = () => {
    navigate('/');
  };

  return (
    <div className="login-container">
      <button 
        onClick={handleBackClick}
        className="back-button"
        disabled={isLoading}
      >
        ← Back to Home
      </button>
      <div className="form-section">
        <h2 className="title">{isLogin ? "Welcome back" : "Create account"}</h2>
        <p className="subtitle">
          {isLogin ? "Sign in to continue" : "Get started"}
        </p>

        {error && (
          <div className="error-message">
            <svg
              className="icon"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          {!isLogin && (
            <div className="name-fields">
              <div className="form-group">
                <label htmlFor="first-name">First Name</label>
                <input
                  id="first-name"
                  name="first_name"
                  type="text"
                  required
                  placeholder="John"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  disabled={isLoading}
                />
              </div>
              <div className="form-group">
                <label htmlFor="last-name">Last Name</label>
                <input
                  id="last-name"
                  name="last_name"
                  type="text"
                  required
                  placeholder="Doe"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  disabled={isLoading}
                />
              </div>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              name="username"
              type="text"
              required
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              disabled={isLoading}
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label htmlFor="email">Email address</label>
              <input
                id="email"
                name="email"
                type="email"
                required
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                disabled={isLoading}
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              required
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={isLogin ? "current-password" : "new-password"}
              disabled={isLoading}
            />
            {!isLogin && (
              <p className="password-hint">
                Password must be at least 8 characters long
              </p>
            )}
          </div>

          {!isLogin && (
            <div className="form-group">
              <label htmlFor="confirm-password">Confirm Password</label>
              <input
                id="confirm-password"
                name="confirm_password"
                type="password"
                required
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={isLoading}
                autoComplete="new-password"
              />
            </div>
          )}

          <div className="button-group">
            <button type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <span className="loading-spinner"></span>
                  {isLogin ? "Signing in..." : "Creating account..."}
                </>
              ) : isLogin ? (
                "Sign in"
              ) : (
                "Create account"
              )}
            </button>

            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError("");
              }}
              className="toggle-button"
              disabled={isLoading}
            >
              {isLogin ? "Need an account? Sign up" : "Already have an account? Sign in"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
