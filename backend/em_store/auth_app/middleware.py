import json
import logging
from django.http import JsonResponse

logger = logging.getLogger('auth_app')

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request details
        logger.debug(f"[Request] {request.method} {request.path}")
        logger.debug(f"[Request Headers] {dict(request.headers)}")
        logger.debug(f"[Request Cookies] {request.COOKIES}")
        
        # Log request body if it exists
        if hasattr(request, '_body') and request.body:
            try:
                body_str = request.body.decode('utf-8')
                logger.debug(f"[Request Body] {body_str[:1000]}")
            except UnicodeDecodeError:
                logger.debug("[Request Body] (binary data)")
        
        # Process the request
        response = self.get_response(request)
        return response
