from django.urls import path
from . import views

app_name = 'auth_app'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('session/', views.session_view, name='session'),
    path('csrf/', views.csrf, name='csrf-token'),
]
