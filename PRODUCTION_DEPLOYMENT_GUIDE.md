# Production Deployment Guide

This guide covers the production deployment configuration for JWT authentication between your Django backend and React frontend on Render.

## Backend (Django) - https://email-automate-ob1a.onrender.com

### Environment Variables to Set in Render Dashboard

Navigate to your Django service in Render and set these environment variables:

#### Required Environment Variables:
```
DJANGO_ENV=production
DEBUG=False
DJANGO_SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
DB_NAME=your_postgres_db_name
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
DB_HOST=your_postgres_host
DB_PORT=5432
```

#### CORS and Security Variables:
```
CORS_ALLOWED_ORIGINS=https://email-automate-1-1hwv.onrender.com
CSRF_TRUSTED_ORIGINS=https://email-automate-1-1hwv.onrender.com,https://email-automate-ob1a.onrender.com
SESSION_COOKIE_DOMAIN=.onrender.com
```

#### Optional Cloudflare R2 Storage (if using):
```
AWS_ACCESS_KEY_ID=your_r2_access_key
AWS_SECRET_ACCESS_KEY=your_r2_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
```

### Security Features Enabled:

1. **HTTPS Only**: All requests redirected to HTTPS
2. **Secure Cookies**: All cookies set with Secure flag
3. **CORS Protection**: Only allows requests from your frontend domain
4. **CSRF Protection**: Configured for cross-origin requests
5. **JWT Token Security**: 
   - Access tokens expire in 1 hour
   - Refresh tokens expire in 7 days
   - Token rotation enabled
   - Blacklist after rotation

## Frontend (React) - https://email-automate-1-1hwv.onrender.com

### Environment Variables to Set in Render Dashboard

Navigate to your React service in Render and set these environment variables:

#### Required Environment Variables:
```
VITE_API_BASE_URL=https://email-automate-ob1a.onrender.com
NODE_ENV=production
NODE_VERSION=18.x
```

### Security Features Implemented:

1. **Secure Token Storage**: JWT tokens stored in localStorage with proper cleanup
2. **Automatic Token Refresh**: Handles token expiration automatically
3. **CORS Headers**: Proper headers for cross-origin requests
4. **Error Handling**: Graceful handling of authentication failures

## JWT Authentication Flow

### Login Process:
1. User submits credentials to `/api/auth/login/`
2. Backend validates credentials and returns JWT tokens
3. Frontend stores tokens securely in localStorage
4. Frontend includes token in Authorization header for subsequent requests

### Token Refresh Process:
1. When access token expires (401 response)
2. Frontend automatically sends refresh token to `/api/auth/refresh/`
3. Backend validates refresh token and returns new access token
4. Frontend updates stored token and retries original request

### Logout Process:
1. Frontend sends refresh token to `/api/auth/logout/`
2. Backend blacklists the refresh token
3. Frontend clears all stored tokens and caches
4. User redirected to login page

## Security Best Practices

### Backend Security:
1. **Environment Variables**: Never commit secrets to version control
2. **HTTPS Only**: All production traffic over HTTPS
3. **CORS Restrictions**: Only allow necessary origins
4. **Token Expiration**: Short-lived access tokens (1 hour)
5. **Token Blacklisting**: Invalidate refresh tokens on logout
6. **Input Validation**: Validate all user inputs
7. **Rate Limiting**: Consider implementing rate limiting for auth endpoints

### Frontend Security:
1. **Token Storage**: Store tokens in localStorage (consider httpOnly cookies for enhanced security)
2. **Token Cleanup**: Clear tokens on logout and errors
3. **HTTPS Only**: Ensure all API calls use HTTPS
4. **Error Handling**: Don't expose sensitive information in error messages
5. **Input Sanitization**: Sanitize user inputs before sending to backend

### Additional Recommendations:

1. **Monitoring**: Set up logging and monitoring for authentication events
2. **Backup**: Regular database backups including JWT blacklist
3. **Updates**: Keep dependencies updated for security patches
4. **Testing**: Test authentication flow thoroughly in production environment
5. **Documentation**: Document any custom authentication logic

## Troubleshooting

### Common Issues:

1. **CORS Errors**: Check that `CORS_ALLOWED_ORIGINS` includes your frontend URL
2. **Token Expiration**: Ensure token refresh is working properly
3. **HTTPS Issues**: Verify all URLs use HTTPS in production
4. **Cookie Issues**: Check SameSite and Secure cookie settings

### Debug Steps:

1. Check browser console for CORS errors
2. Verify environment variables are set correctly in Render
3. Check Django logs for authentication errors
4. Test API endpoints directly with tools like Postman
5. Verify JWT token format and expiration

## Testing the Deployment

1. **Test Login**: Verify users can log in successfully
2. **Test Token Refresh**: Wait for token expiration and verify automatic refresh
3. **Test Logout**: Verify tokens are properly cleared
4. **Test Protected Routes**: Ensure authenticated users can access protected content
5. **Test Unauthorized Access**: Verify unauthenticated users are redirected to login

## Environment Variable Reference

### Backend Variables:
- `DJANGO_ENV`: Set to 'production'
- `DEBUG`: Set to 'False'
- `DJANGO_SECRET_KEY`: Long, random secret key
- `DB_*`: PostgreSQL database connection details
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins
- `CSRF_TRUSTED_ORIGINS`: Comma-separated list of trusted origins
- `SESSION_COOKIE_DOMAIN`: Domain for session cookies

### Frontend Variables:
- `VITE_API_BASE_URL`: Backend API URL
- `NODE_ENV`: Set to 'production'
- `NODE_VERSION`: Node.js version (18.x recommended)

## Next Steps

1. Deploy both services to Render
2. Set all environment variables in Render dashboard
3. Test the complete authentication flow
4. Monitor logs for any issues
5. Set up monitoring and alerting
6. Document any custom configurations 