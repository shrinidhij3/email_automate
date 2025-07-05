import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import "./App.css";
import Home from "./components/Home";
import EmailDashboard from "./components/EmailDashboard";
import UnreadEmailsDashboard from "./components/UnreadEmailsDashboard";
import EmailMain from "./components/EmailMain";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./components/LoginPage";
import Navbar from "./components/Navbar";
import "./components/Navbar.css";

// Main app layout with Navbar and content
const AppLayout = () => {
  return (
    <div className="app">
      <Navbar />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

// Wrapper for protected routes
const ProtectedRouteWrapper = () => {
  return (
    <ProtectedRoute>
      <Outlet />
    </ProtectedRoute>
  );
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public routes without layout */}
          <Route path="/login" element={<LoginPage />} />
          
          {/* Routes with layout */}
          <Route element={<AppLayout />}>
            <Route index element={<Home />} />
            <Route path="unread-emails" element={<UnreadEmailsDashboard />} />
            
            {/* Protected routes */}
            <Route element={<ProtectedRouteWrapper />}>
              <Route path="dashboard/upload" element={<EmailMain />} />
              <Route path="email-dashboard" element={<EmailDashboard />} />
            </Route>
            
            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
