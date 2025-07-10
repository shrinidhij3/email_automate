import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Navbar.css';

const Navbar: React.FC = () => {
  const { logout, isAuthenticated } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleNavClick = (path: string) => {
    setMenuOpen(false);
    if (path === '/dashboard/upload' && !isAuthenticated) {
      navigate('/login');
    } else {
      navigate(path);
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/" className="logo">
          Email Automation
        </Link>
        <button className="hamburger" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle navigation">
          <span className="bar"></span>
          <span className="bar"></span>
          <span className="bar"></span>
        </button>
      </div>
      <div className={`navbar-links${menuOpen ? ' open' : ''}`}>
        {isAuthenticated ? (
          <>
            <button className="nav-link" onClick={() => handleNavClick('/login')}>Create Campaign</button>
            <Link to="/unread-emails" className="nav-link">Email Auto Reply</Link>
            <button className="logout-btn" onClick={logout}>
              Logout
            </button>
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
