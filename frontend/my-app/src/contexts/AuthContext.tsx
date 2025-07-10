import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import authService from '../services/authService';

// Define interfaces locally to avoid import issues
interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name?: string;
  last_name?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const authCheckRef = useRef<Promise<boolean> | null>(null);

  const checkAuth = async (): Promise<boolean> => {
    // Prevent multiple simultaneous auth checks
    if (authCheckRef.current) {
      console.log('Auth check already in progress, waiting...');
      return authCheckRef.current;
    }

    const authPromise = (async () => {
      try {
        console.log('Starting auth check...');
        
        // Check if we have a token first
        const token = localStorage.getItem('access_token');
        if (!token) {
          console.log('No access token found');
          setUser(null);
          setIsAuthenticated(false);
          setIsLoading(false);
          return false;
        }

        // Get current user without forcing refresh
        const currentUser = await authService.getCurrentUser(false);
        if (currentUser) {
          console.log('User authenticated:', currentUser.username);
          setUser(currentUser);
          setIsAuthenticated(true);
        } else {
          console.log('No valid user found');
          setUser(null);
          setIsAuthenticated(false);
        }
        
        setIsLoading(false);
        return !!currentUser;
      } catch (error) {
        console.error('Auth check failed:', error);
        setUser(null);
        setIsAuthenticated(false);
        setIsLoading(false);
        return false;
      }
    })();

    authCheckRef.current = authPromise;
    const result = await authPromise;
    authCheckRef.current = null;
    return result;
  };

  const login = async (username: string, password: string) => {
    try {
      console.log('Attempting login...');
      const response = await authService.login(username, password);
      
      setUser(response.user);
      setIsAuthenticated(true);
      console.log('Login successful');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (userData: RegisterData) => {
    try {
      console.log('Attempting registration...');
      const response = await authService.register(userData);
      
      setUser(response.user);
      setIsAuthenticated(true);
      console.log('Registration successful');
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      console.log('Logging out...');
      await authService.logout();
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
      // Even if logout fails, clear local state
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  // Only check auth once on mount
  useEffect(() => {
    console.log('AuthProvider mounted, checking auth...');
    checkAuth();
  }, []); // Empty dependency array - only run once

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

