from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import get_csrf_token

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'email-campaigns', views.EmailCampaignViewSet, basename='email-campaign')
router.register(r'attachments', views.CampaignEmailAttachmentViewSet, basename='attachment')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    # CSRF token endpoint
    path('csrf-token/', get_csrf_token, name='get_csrf_token'),
]
