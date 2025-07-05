import React, { useEffect } from "react";
import EmailConfigForm from "./EmailConfigForm";
import "./EmailConfigForm.css";

const UnreadEmailsDashboard: React.FC = () => {
  // Ensure the root element has proper height
  useEffect(() => {
    document.documentElement.style.height = '100%';
    document.body.style.height = '100%';
    document.body.style.margin = '0';
    document.body.style.overflow = 'hidden';
    
    return () => {
      document.documentElement.style.height = '';
      document.body.style.height = '';
      document.body.style.margin = '';
      document.body.style.overflow = '';
    };
  }, []);

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#f5f5f5',
      overflow: 'hidden'
    }}>
      <div style={{
        maxWidth: '1000px',
        width: '100%',
        margin: '0 auto',
        padding: '1rem',
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        <header style={{
          padding: '0.5rem 0',
          marginBottom: '1rem',
          flexShrink: 0
        }}>
          <h1 style={{
            margin: 0,
            color: '#2c3e50',
            fontSize: '1.8rem',
            lineHeight: 1.2
          }}>Email Configuration</h1>
        </header>
        
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          minHeight: 0,
          overflow: 'hidden',
          position: 'relative'
        }}>
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            overflowY: 'auto',
            paddingRight: '0.5rem'
          }}>
            <EmailConfigForm />
          </div>
        </div>
      </div>
    </div>
  );
};

export default UnreadEmailsDashboard;
