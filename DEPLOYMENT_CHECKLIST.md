# Deployment Checklist

## Pre-Deployment Checklist

### Backend (Django) Configuration ✅
- [x] Updated `production_settings.py` with proper CORS and JWT settings
- [x] Updated `settings.py` with environment variable overrides
- [x] Updated auth views with proper CORS headers and CSRF exemption
- [x] Configured JWT token settings for production security

### Frontend (React) Configuration ✅
- [x] Updated API configuration with `withCredentials: true`
- [x] Enhanced auth service with secure token management
- [x] Updated AuthContext to use enhanced auth service
- [x] Configured automatic token refresh handling
- [x] Updated `render.yaml` with correct API base URL

## Render Dashboard Configuration

### Backend Environment Variables
- [ ] `DJANGO_ENV=production`
- [ ] `DEBUG=False`
- [ ] `DJANGO_SECRET_KEY=<your-secret-key>`
- [ ] `DB_NAME=<your-db-name>`
- [ ] `DB_USER=<your-db-user>`
- [ ] `DB_PASSWORD=<your-db-password>`
- [ ] `DB_HOST=<your-db-host>`
- [ ] `DB_PORT=5432`
- [ ] `CORS_ALLOWED_ORIGINS=https://email-automate-1-1hwv.onrender.com`
- [ ] `CSRF_TRUSTED_ORIGINS=https://email-automate-1-1hwv.onrender.com,https://email-automate-ob1a.onrender.com`
- [ ] `SESSION_COOKIE_DOMAIN=.onrender.com`

### Frontend Environment Variables
- [ ] `VITE_API_BASE_URL=https://email-automate-ob1a.onrender.com`
- [ ] `NODE_ENV=production`
- [ ] `NODE_VERSION=18.x`

## Security Verification

### Backend Security ✅
- [x] HTTPS redirect enabled
- [x] Secure cookies configured
- [x] CORS properly configured for frontend domain
- [x] CSRF protection configured
- [x] JWT token security settings applied
- [x] Token blacklisting enabled

### Frontend Security ✅
- [x] Secure token storage implemented
- [x] Automatic token refresh configured
- [x] Proper error handling for auth failures
- [x] Token cleanup on logout
- [x] HTTPS API calls enforced

## Testing Checklist

### Authentication Flow
- [ ] User registration works
- [ ] User login works
- [ ] JWT tokens are properly stored
- [ ] Protected routes require authentication
- [ ] Token refresh works automatically
- [ ] Logout properly clears tokens
- [ ] Unauthorized access redirects to login

### Cross-Origin Requests
- [ ] CORS headers are properly set
- [ ] Preflight requests work
- [ ] Credentials are included in requests
- [ ] No CORS errors in browser console

### Security Testing
- [ ] HTTPS is enforced
- [ ] Secure cookies are set
- [ ] JWT tokens expire correctly
- [ ] Invalid tokens are rejected
- [ ] Logout blacklists refresh tokens

## Monitoring Setup

### Logging
- [ ] Django logs are accessible
- [ ] Authentication events are logged
- [ ] Error logs are monitored
- [ ] CORS errors are tracked

### Performance
- [ ] API response times are acceptable
- [ ] Token refresh doesn't cause delays
- [ ] Database connections are optimized

## Post-Deployment Verification

### URLs to Test
- [ ] Backend: https://email-automate-ob1a.onrender.com/admin/
- [ ] Frontend: https://email-automate-1-1hwv.onrender.com
- [ ] API endpoints: https://email-automate-ob1a.onrender.com/api/auth/

### Browser Testing
- [ ] Test in Chrome
- [ ] Test in Firefox
- [ ] Test in Safari
- [ ] Test on mobile devices

### Error Monitoring
- [ ] Check for 500 errors
- [ ] Monitor authentication failures
- [ ] Track CORS issues
- [ ] Watch for token expiration issues

## Rollback Plan

### If Issues Occur
1. [ ] Check Render logs for errors
2. [ ] Verify environment variables are set correctly
3. [ ] Test API endpoints directly
4. [ ] Check browser console for CORS errors
5. [ ] Verify database connectivity
6. [ ] Check JWT token format and expiration

### Emergency Rollback
- [ ] Keep previous deployment as backup
- [ ] Document current working configuration
- [ ] Have rollback procedure ready

## Documentation

### Updated Files
- [x] `em_store/production_settings.py`
- [x] `em_store/settings.py`
- [x] `auth_app/views.py`
- [x] `src/api/api.ts`
- [x] `src/services/authService.ts`
- [x] `src/contexts/AuthContext.tsx`
- [x] `render.yaml`
- [x] `PRODUCTION_DEPLOYMENT_GUIDE.md`
- [x] `DEPLOYMENT_CHECKLIST.md`

### Next Steps
1. [ ] Deploy backend to Render
2. [ ] Deploy frontend to Render
3. [ ] Set environment variables in Render dashboard
4. [ ] Test complete authentication flow
5. [ ] Monitor for any issues
6. [ ] Document any custom configurations 