export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthSuccessResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  message?: string;
}

export interface AuthErrorResponse {
  error?: string;
  message?: string;
  [key: string]: any;
}

export interface ErrorResponse {
  error?: string;
  [key: string]: any;
} 