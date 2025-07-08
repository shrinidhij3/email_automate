import type { ReactNode } from 'react';
import { useEffect, useState } from 'react';
import { Navigate, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children?: ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isLoading, checkAuth } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [authChecked, setAuthChecked] = useState(false);
  const [isAuth, setIsAuth] = useState<boolean | null>(null);

  useEffect(() => {
    const verifyAuth = async () => {
      try {
        const isUserAuthenticated = await checkAuth();
        setIsAuth(isUserAuthenticated);
        
        if (!isUserAuthenticated) {
          // Only redirect if not already on login page to prevent loops
          if (location.pathname !== '/login') {
            navigate('/login', { 
              state: { from: location },
              replace: true 
            });
          }
        }
      } catch (error) {
        console.error('Auth verification error:', error);
        setIsAuth(false);
        navigate('/login', { 
          state: { from: location },
          replace: true 
        });
      } finally {
        setAuthChecked(true);
      }
    };

    verifyAuth();
  }, [checkAuth, location, navigate]);

  if (isLoading || !authChecked) {
    return <div>Loading...</div>;
  }

  if (isAuth === false) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children ? <>{children}</> : <Outlet />;
};

export default ProtectedRoute;
