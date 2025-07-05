from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver
from pprint import pprint
import io
import sys

class TestAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_urls(self, urlpatterns, prefix=''):
        """Recursively get all URLs"""
        result = []
        for pattern in urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                # This is an include()
                result.extend(self.get_urls(pattern.url_patterns, prefix + str(pattern.pattern)))
            else:
                # This is a URL pattern
                result.append({
                    'pattern': f"{prefix}{pattern.pattern}",
                    'name': pattern.name or 'No name',
                    'callback': getattr(pattern, 'callback', None),
                })
        return result
    
    def get(self, request):
        # Get all URLs
        resolver = get_resolver()
        urls = self.get_urls(resolver.url_patterns)
        
        # Get installed apps
        from django.conf import settings
        
        return Response({
            "message": "Test GET endpoint is working!",
            "urls": urls,
            "installed_apps": settings.INSTALLED_APPS,
            "debug": settings.DEBUG,
        })
    
    def post(self, request):
        # Get all URLs
        resolver = get_resolver()
        urls = self.get_urls(resolver.url_patterns)
        
        return Response({
            "message": "Test POST endpoint is working!",
            "data_received": request.data,
            "urls": urls
        })
