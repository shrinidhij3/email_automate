from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from . import views
from .api_views import CampaignEmailAttachmentViewSet

# Main router for campaigns
router = DefaultRouter()
router.register(r'', views.EmailCampaignViewSet, basename='emailcampaign')

# Separate router for attachments
attachments_router = SimpleRouter()
attachments_router.register(r'attachments', CampaignEmailAttachmentViewSet, basename='attachment')

urlpatterns = [
    # Include both routers
    path('', include(router.urls)),
    path('<int:campaign_pk>/', include(attachments_router.urls)),
    
    # Add the download URL with a custom action
    path(
        '<int:campaign_pk>/attachments/<int:pk>/download/',
        CampaignEmailAttachmentViewSet.as_view({'get': 'download'}),
        name='attachment-download'
    ),
    # Add the upload URL
    path(
        '<int:pk>/upload/',
        CampaignEmailAttachmentViewSet.as_view({'post': 'upload'}),
        name='attachment-upload'
    ),
]
