from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Register the viewset with an empty prefix since we're already namespaced under /api/campaigns/
router.register(r'', views.EmailCampaignViewSet, basename='emailcampaign')

urlpatterns = [
    path('', include(router.urls)),
]
