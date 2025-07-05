from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
import json

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
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'email': user.email
        })
    return JsonResponse(
        {'error': 'Invalid credentials'}, 
        status=400
    )

@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Successfully logged out'})

def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})

def session_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})
        
    return JsonResponse({
        'isAuthenticated': True,
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email
    })
