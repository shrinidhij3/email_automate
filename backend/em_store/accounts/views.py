from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

class RegisterView(generics.CreateAPIView):
    """
    Register a new user.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Log the user in after registration
            login(request, user)
            return Response(
                {"detail": "User registered successfully."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    Login a user and return a session cookie.
    """
    permission_classes = [permissions.AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {"detail": "Please provide both username and password"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return Response({"detail": "Successfully logged in."})
            else:
                return Response(
                    {"detail": "This account is not active."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

class LogoutView(APIView):
    """
    Logout the current user.
    """
    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"detail": "Successfully logged out."})

class SessionView(APIView):
    """
    Get the current user's session information.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        return Response({
            'isAuthenticated': request.user.is_authenticated,
            'username': request.user.username,
            'email': request.user.email,
            'firstName': request.user.first_name,
            'lastName': request.user.last_name,
        })

class CSRFView(APIView):
    """
    Get CSRF token for the frontend.
    """
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        return Response({"detail": "CSRF cookie set"})
