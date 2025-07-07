import axios from 'axios';
import { API_BASE_URL } from '../config/api';

export async function fetchCSRFToken(): Promise<string> {
  const response = await axios.get(`${API_BASE_URL}/api/csrf-token/`, {
    withCredentials: true,
    headers: {
      'Accept': 'application/json',
      'Cache-Control': 'no-cache',
      'Pragma': 'no-cache'
    }
  });
  
  if (!response.data?.csrfToken) {
    throw new Error('No CSRF token received');
  }
  
  // Set the token in cookies for future requests
  document.cookie = `csrftoken=${response.data.csrfToken}; path=/`;
  
  return response.data.csrfToken;
}
