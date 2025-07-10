from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, LogoutView, user_view

app_name = 'auth_app'

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', user_view, name='user'),
    # JWT token refresh endpoint
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
