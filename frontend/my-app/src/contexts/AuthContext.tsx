import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';

export interface User {
  id: number;
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (
    username: string, 
    email: string, 
    password: string,
    password2: string,
    firstName: string,
    lastName: string
  ) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<boolean>;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Check authentication status
  const checkAuth = useCallback(async (): Promise<boolean> => {
    try {
      const isAuth = await authService.isAuthenticated();
      if (isAuth) {
        const userData = await authService.getCurrentUser();
        setUser(userData);
        return true;
      }
      setUser(null);
      return false;
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
      return false;
    }
  }, []);

  // Check for existing session on initial load
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        await checkAuth();
      } catch (error) {
        console.error('Initial auth check failed:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, [checkAuth]);

  const login = async (username: string, password: string) => {
    try {
      setError(null);
      setIsLoading(true);
      const userData = await authService.login(username, password);
      setUser(userData);
      navigate('/dashboard/upload');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Login failed';
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (
    username: string,
    email: string,
    password: string,
    password2: string,
    firstName: string,
    lastName: string
  ) => {
    try {
      setError(null);
      setIsLoading(true);
      const userData = await authService.register(
        username,
        email,
        password,
        password2,
        firstName,
        lastName
      );
      setUser(userData);
      navigate('/dashboard/upload');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Registration failed';
      setError(message);
      throw error; // Re-throw to allow component to handle specific errors
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);
      await authService.logout();
      setUser(null);
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    checkAuth,
    error,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
