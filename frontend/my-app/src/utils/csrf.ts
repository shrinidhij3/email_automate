import axios from 'axios';
import { API_BASE_URL } from '../config/api';

/**
 * Fetches a new CSRF token from the server
 * @returns Promise that resolves to the CSRF token string
 * @throws Error if the token cannot be retrieved
 */
export async function fetchCSRFToken(): Promise<string> {
  try {
    console.log('[CSRF] Fetching CSRF token from:', `${API_BASE_URL}/api/csrf-token/`);
    
    const response = await axios.get(`${API_BASE_URL}/api/csrf-token/`, {
      withCredentials: true,  // Required for cross-domain cookies
      headers: {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'X-Requested-With': 'XMLHttpRequest'
      },
      timeout: 10000  // 10 second timeout
    });
    
    if (!response?.data?.csrfToken) {
      console.error('[CSRF] Invalid response format:', response);
      throw new Error('Invalid response from server');
    }
    
    console.log('[CSRF] Token received successfully');
    return response.data.csrfToken;
  } catch (error: unknown) {
    let errorMessage = 'Failed to get security token';
    
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      const responseData = error.response?.data;
      
      console.error('[CSRF] Error details:', {
        status,
        message: error.message,
        response: responseData,
        url: error.config?.url,
        method: error.config?.method,
      });
      
      if (status === 403) {
        errorMessage = 'Session expired. Please refresh the page and try again.';
      } else if (status === 404) {
        errorMessage = 'Authentication service unavailable. Please try again later.';
      } else if (status && status >= 500) {
        errorMessage = 'Server error. Please try again in a few moments.';
      }
    } else if (error instanceof Error) {
      console.error('[CSRF] Unexpected error:', error);
      errorMessage = error.message || errorMessage;
    } else {
      console.error('[CSRF] Unknown error:', error);
    }
    
    throw new Error(errorMessage);
  }
}
