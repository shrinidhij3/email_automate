import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface AuthFormValues {
  username: string;
  email: string;
  password: string;
}

const useAuthForm = (isLogin: boolean = false) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login, register } = useAuth();

  const handleSubmit = async (
    values: AuthFormValues,
    onSuccess?: () => void
  ) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const { username, email, password } = values;
      
      if (isLogin) {
        await login(username, password);
      } else {
        if (!email) {
          throw new Error('Email is required for registration');
        }
        await register(username, email, password, '', '', ''); // Added empty strings for missing required arguments
      }
      
      onSuccess?.();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    handleSubmit,
    isSubmitting,
    error,
  };
};

export default useAuthForm;
