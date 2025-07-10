from django.middleware.csrf import CsrfViewMiddleware
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.middleware.csrf import get_token
import re

class CustomCSRFMiddleware(MiddlewareMixin):
    """
    Custom CSRF middleware that excludes API endpoints from CSRF protection.
    This allows the admin panel to work while keeping API endpoints CSRF-free.
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.csrf_middleware = CsrfViewMiddleware(get_response)
    
    def process_request(self, request):
        # Check if the request path matches API endpoints
        if re.match(r'^/api/', request.path):
            # Skip CSRF for API endpoints
            return None
        
        # Apply CSRF for all other endpoints (including admin)
        if request.method == 'GET':
            get_token(request)
        return self.csrf_middleware.process_request(request)
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Check if the request path matches API endpoints
        if re.match(r'^/api/', request.path):
            # Skip CSRF for API endpoints
            return None
        
        # Apply CSRF for all other endpoints (including admin)
        return self.csrf_middleware.process_view(request, callback, callback_args, callback_kwargs)
    
    def process_response(self, request, response):
        # Check if the request path matches API endpoints
        if re.match(r'^/api/', request.path):
            # Skip CSRF for API endpoints
            return response
        
        # Apply CSRF for all other endpoints (including admin)
        return self.csrf_middleware.process_response(request, response) 