import json
import logging
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Get an instance of a logger
logger = logging.getLogger('auth_app')

def log_request(request, prefix=""):
    """Log request details"""
    logger.debug(f"{prefix}Request: {request.method} {request.path}")
    logger.debug(f"{prefix}Headers: {dict(request.headers)}")
    logger.debug(f"{prefix}Cookies: {request.COOKIES}")
    if request.body:
        try:
            logger.debug(f"{prefix}Body: {request.body.decode('utf-8')}")
        except:
            logger.debug(f"{prefix}Body: (binary data)")

def log_response(response, prefix=""):
    """Log response details"""
    logger.debug(f"{prefix}Response: {response.status_code}")
    logger.debug(f"{prefix}Response Headers: {dict(response.headers)}")
    if hasattr(response, 'content'):
        try:
            logger.debug(f"{prefix}Response Content: {response.content.decode('utf-8')}")
        except:
            logger.debug(f"{prefix}Response Content: (binary data)")

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # No authentication required for registration

    def post(self, request, *args, **kwargs):
        logger.debug("RegisterView called for registration request")
        logger.debug(f"Request method: {request.method}")
        logger.debug(f"Request path: {request.path}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.debug(f"Registration successful for user: {user.username}")
            
            # Generate JWT tokens for the new user
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            response_data = {
                "detail": "Registration successful. Please log in.",
                "access_token": str(access_token),
                "refresh_token": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            }
            
            response = Response(response_data, status=status.HTTP_201_CREATED)
            return response
        
        logger.debug(f"Registration failed: {serializer.errors}")
        response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return response

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]  # No authentication required for login

    def post(self, request, *args, **kwargs):
        logger.debug("LoginView called")
        logger.debug(f"Request method: {request.method}")
        logger.debug(f"Request path: {request.path}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            logger.debug(f"Login successful for user: {username}")
            logger.debug(f"Generated JWT tokens for user: {username}")
            
            response_data = {
                "detail": "Successfully logged in.",
                "access_token": str(access_token),
                "refresh_token": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name or '',
                    "last_name": user.last_name or ''
                }
            }
            
            response = Response(response_data)
            return response
        
        logger.debug(f"Login failed for username: {username}")
        response = Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
        return response

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Blacklist the refresh token if provided
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                logger.debug("Refresh token blacklisted")
            
            response = Response({"detail": "Successfully logged out."})
            return response
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            response = Response({"detail": "Logout successful."})
            return response

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def user_view(request):
    # Get the origin from the request
    # origin = request.headers.get('Origin', '')
    # allowed_origins = [
    #     'http://localhost:3000',
    #     'http://localhost:5173',
    #     'https://email-automate-1-1hwv.onrender.com',
    # ]
    # is_allowed_origin = any(origin.startswith(allowed) for allowed in allowed_origins)

    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = JsonResponse({}, status=200)
        # if is_allowed_origin:
        #     response['Access-Control-Allow-Origin'] = origin
        #     response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        #     response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Cache-Control, Pragma'
        #     response['Access-Control-Allow-Credentials'] = 'true'
        #     response['Access-Control-Max-Age'] = '86400'
        #     response['Vary'] = 'Origin'
        return response
    
    # Handle GET request
    if request.method == 'GET':
        try:
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            user_data = {
                'status': 'success',
                'user': {
                    'is_authenticated': user is not None,
                    'username': user.username if user else None,
                    'email': user.email if user else None,
                    'first_name': user.first_name if user else None,
                    'last_name': user.last_name if user else None,
                }
            }
            response = JsonResponse(user_data)
            # if is_allowed_origin:
            #     response['Access-Control-Allow-Origin'] = origin
            #     response['Access-Control-Allow-Credentials'] = 'true'
            #     response['Vary'] = 'Origin'
            return response
                
        except Exception as e:
            logger.error(f"Error in user_view: {str(e)}")
            response = JsonResponse(
                {'status': 'error', 'message': 'Failed to get user data'},
                status=500
            )
            # if is_allowed_origin:
            #     response['Access-Control-Allow-Origin'] = origin
            #     response['Access-Control-Allow-Credentials'] = 'true'
            #     response['Vary'] = 'Origin'
            return response
