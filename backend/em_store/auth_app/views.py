import json
import logging
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.conf import settings

# Get an instance of a logger
logger = logging.getLogger('auth_app')

def log_request(request, prefix=""):
    """Log request details"""
    logger.debug(f"{prefix}Request: {request.method} {request.path}")
    logger.debug(f"{prefix}Headers: {dict(request.headers)}")
    logger.debug(f"{prefix}Cookies: {request.COOKIES}")
    logger.debug(f"{prefix}Session: {dict(request.session)}")
    if request.body:
        try:
            logger.debug(f"{prefix}Body: {request.body.decode('utf-8')}")
        except:
            logger.debug(f"{prefix}Body: (binary data)")

def log_response(response, prefix=""):
    """Log response details"""
    logger.debug(f"{prefix}Response: {response.status_code}")
    logger.debug(f"{prefix}Response Headers: {dict(response.headers)}")
    if hasattr(response, 'cookies') and response.cookies:
        logger.debug(f"{prefix}Response Cookies: {response.cookies}")
    if hasattr(response, 'content'):
        try:
            logger.debug(f"{prefix}Response Content: {response.content.decode('utf-8')}")
        except:
            logger.debug(f"{prefix}Response Content: (binary data)")

@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        password2 = data.get('password2', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        # Validate required fields
        if not all([username, email, password, password2]):
            return JsonResponse(
                {'error': 'Please provide all required fields'}, 
                status=400
            )
            
        # Check if passwords match
        if password != password2:
            return JsonResponse(
                {'error': 'Passwords do not match'}, 
                status=400
            )
            
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {'error': 'Username already exists'}, 
                status=400
            )
            
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {'error': 'Email already registered'}, 
                status=400
            )
            
        # Create user with additional fields
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Log the user in
        login(request, user)
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
        
    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Invalid JSON data'}, 
            status=400
        )
    except IntegrityError as e:
        return JsonResponse(
            {'error': 'Database error: ' + str(e)}, 
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {'error': str(e)}, 
            status=500
        )

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        # Debugging request body
        print(f"[DEBUG] Raw body: {repr(request.body)}")
        print(f"[DEBUG] Content-Length: {request.META.get('CONTENT_LENGTH')}")
        print(f"[DEBUG] Content-Type: {request.META.get('CONTENT_TYPE')}")
        print(f"[DEBUG] Request method: {request.method}")
        print(f"[DEBUG] Request headers: {dict(request.headers)}")
        
        # Log to file
        logger.debug(f"[Login] Raw body: {repr(request.body)}")
        logger.debug(f"[Login] Content-Length: {request.META.get('CONTENT_LENGTH')}")
        logger.debug(f"[Login] Request method: {request.method}")
        logger.debug(f"[Login] Request headers: {dict(request.headers)}")
        logger.debug(f"[Login] Request META: { {k: v for k, v in request.META.items() if k.startswith('HTTP_')} }")
        
        # Handle empty body
        if not request.body or request.body == b'':
            error_msg = 'Empty request body received'
            print(f"[ERROR] {error_msg}")
            logger.error(error_msg)
            return JsonResponse(
                {'error': error_msg, 'details': 'The server received an empty request body'}, 
                status=400
            )
        
        # Try to parse JSON
        try:
            body_str = request.body.decode('utf-8')
            print(f"[DEBUG] Decoded body string: {body_str[:200]}...")
            data = json.loads(body_str)
        except UnicodeDecodeError as e:
            error_msg = f'Invalid request encoding: {str(e)}'
            print(f"[ERROR] {error_msg}")
            logger.error(error_msg)
            return JsonResponse(
                {'error': 'Invalid request encoding', 'details': str(e)}, 
                status=400
            )
        except json.JSONDecodeError as e:
            error_msg = f'Invalid JSON: {str(e)}'
            print(f"[ERROR] {error_msg}")
            print(f"[DEBUG] Problematic JSON: {body_str[:200]}...")
            logger.error(f"{error_msg}\nProblematic JSON: {body_str[:200]}...")
            return JsonResponse(
                {'error': 'Invalid JSON format', 'details': str(e)}, 
                status=400
            )
        
        # Get credentials
        username = data.get('username')
        password = data.get('password')
        
        # Validate credentials
        if not username or not password:
            logger.error("[Login] Missing username or password")
            return JsonResponse(
                {'error': 'Username and password are required'}, 
                status=400
            )
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Log the user in
            login(request, user)
            logger.info(f"[Login] User authenticated: {user.username}")
            
            # Create response
            response = JsonResponse({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
            
            # Log response
            log_response(response, "[Login Success] ")
            return response
            
        logger.warning(f"[Login] Invalid credentials for user: {username}")
        return JsonResponse(
            {'error': 'Invalid credentials'}, 
            status=400
        )
        
    except Exception as e:
        logger.exception("[Login] Unexpected error:")
        return JsonResponse(
            {'error': 'An error occurred during login'}, 
            status=500
        )

@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Successfully logged out'})

@csrf_exempt
def csrf(request):
    """Get CSRF token with detailed logging"""
    log_request(request, "[CSRF] ")
    
    # Get the CSRF token
    csrf_token = get_token(request)
    
    # Prepare the response
    response = JsonResponse({'csrfToken': csrf_token})
    
    # Log the response before sending
    log_response(response, "[CSRF] ")
    
    # Log the cookies being set
    logger.debug(f"[CSRF] Setting CSRF cookie: {response.cookies}")
    logger.debug(f"[CSRF] Session ID in request: {request.session.session_key}")
    
    return response

@csrf_exempt
def session_view(request):
    """Check session status with detailed logging"""
    log_request(request, "[SESSION] ")
    
    if not request.user.is_authenticated:
        logger.debug("[SESSION] User not authenticated")
        response = JsonResponse({'isAuthenticated': False})
    else:
        logger.debug(f"[SESSION] User authenticated: {request.user.username}")
        response = JsonResponse({
            'isAuthenticated': True,
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email
        })
    
    # Log the response
    log_response(response, "[SESSION] ")
    
    # Add CORS headers
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Allow-Origin'] = request.headers.get('Origin', '')
    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken, X-Requested-With'
    
    return response
