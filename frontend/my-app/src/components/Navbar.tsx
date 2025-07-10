import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar: React.FC = () => {
  const { logout, isAuthenticated } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/" className="logo">
          Email Campaign
        </Link>
      </div>
      <div className="navbar-links">
        {isAuthenticated ? (
          <>
            <Link to="/dashboard/upload" className="nav-link">Create Campaign</Link>
            <Link to="/unread-emails" className="nav-link">Unread Emails</Link>
            {isAuthenticated && (
              <button className="logout-btn" onClick={logout} style={{ marginLeft: '1rem' }}>
                Logout
              </button>
            )}
          </>
        ) : (
          <>
            <Link to="/login" className="nav-link">Login</Link>
            <Link to="/register" className="btn btn-primary">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
