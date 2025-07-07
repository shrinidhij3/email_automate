import axios from 'axios';
import { API_BASE_URL } from '../config/api';

export async function fetchCSRFToken(): Promise<string> {
  try {
    console.log('Fetching CSRF token from:', `${API_BASE_URL}/api/csrf-token/`);
    
    const response = await axios.get(`${API_BASE_URL}/api/csrf-token/`, {
      withCredentials: true,  // Important for sending/receiving cookies cross-domain
      headers: {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest'
      }
    });
    
    if (!response.data?.csrfToken) {
      throw new Error('No CSRF token received from server');
    }
    
    console.log('CSRF token received, checking cookies...');
    
    // In cross-domain, we don't need to manually set the cookie
    // The server will set it with the correct domain and flags
    
    // Just verify we can read the cookie
    const csrfCookie = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
      
    if (!csrfCookie) {
      console.warn('CSRF cookie not found in document.cookies after fetch');
    } else {
      console.log('CSRF cookie is available in document.cookies');
    }
    
    return response.data.csrfToken;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      console.error('Error fetching CSRF token:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        headers: error.response?.headers
      });
    } else if (error instanceof Error) {
      console.error('Error fetching CSRF token:', error.message);
    } else {
      console.error('Unknown error fetching CSRF token:', error);
    }
    throw new Error('Failed to get security token. Please refresh the page and try again.');
  }
}
