from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import save_email_config
from .views import download_attachment, UnreadEmailViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'submissions', UnreadEmailViewSet, basename='unreademail')

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # Email configuration endpoint (legacy)
    path('', save_email_config, name='save-email-config'),
    
    # Attachment download endpoint
    path('attachments/<int:attachment_id>/download/', 
         download_attachment, 
         name='download-attachment'),
]
