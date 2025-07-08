from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'email-campaigns', views.EmailCampaignViewSet, basename='email-campaign')
router.register(r'attachments', views.CampaignEmailAttachmentViewSet, basename='attachment')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
