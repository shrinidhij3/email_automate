

"""
URL configuration for em_store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Local imports
from . import views
from .views import DebugURLsView, TestAdminView, landing_page
from unread_emails.views import AdminSubmissionListView

# API imports
from api.views import get_csrf_token, get_current_user

# Schema view for API documentation
schema_view = get_schema_view(
   openapi.Info(
      title="Email Campaigns API",
      default_version='v1',
      description="API documentation for Email Campaigns",
      terms_of_service="https://www.yourapp.com/terms/",
      contact=openapi.Contact(email="contact@yourapp.com"),
      license=openapi.License(name="Your License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Landing page
    path('', landing_page, name='landing_page'),
    
    # Django admin
    path('admin/', admin.site.urls),
    
    # Debug and test URLs
    path('debug/urls/', DebugURLsView.as_view(), name='debug-urls'),
    path('test/admin/', TestAdminView.as_view(), name='test-admin'),
    
    # Admin submissions page - using a non-conflicting path
    path('submissions/admin/', AdminSubmissionListView.as_view(), name='admin-submissions'),
    
    # Redirect root to API documentation
    path('', RedirectView.as_view(url='/api/docs/', permanent=False), name='home'),
    
    # Authentication endpoints - all under /api/auth/
    path('api/auth/', include('auth_app.urls')),
    
    # API endpoints
    path('api/accounts/', include('accounts.urls')),  # User accounts API
    path('api/email-entries/', include('email_entry.urls')),  # Email entries API
    path('api/unread-emails/', include('unread_emails.urls')),  # Unread emails API
    path('api/campaigns/', include('campaigns.urls')),  # Email campaigns API
    
    # API Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Standardized CSRF token endpoint
    path('api/auth/csrf-token/', get_csrf_token, name='get_csrf_token'),
    
    # Include API app URLs (keep this last to avoid overriding other routes)
    path('api/', include('api.urls')),
    
    # Debug endpoint
    path('debug/urls/', views.list_urls, name='list-urls'),  # Debug URL to list all URLs
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
