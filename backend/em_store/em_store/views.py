from django.http import HttpResponse, JsonResponse
from django.urls import get_resolver, reverse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

def landing_page(request):
    """Render the landing page"""
    return render(request, 'emails/index.html')


def list_urls(request):
    """List all URLs in the project"""
    def get_urls(urlpatterns, prefix=''):
        result = []
        for pattern in urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                # This is an include()
                result.extend(get_urls(pattern.url_patterns, prefix + str(pattern.pattern)))
            else:
                # This is a URL pattern
                result.append({
                    'pattern': f"{prefix}{pattern.pattern}",
                    'name': pattern.name or 'No name',
                    'callback': f"{pattern.callback.__module__}.{pattern.callback.__name__}" if hasattr(pattern, 'callback') else 'No callback',
                })
        return result
    
    resolver = get_resolver()
    urls = get_urls(resolver.url_patterns)
    return JsonResponse({'urls': urls})


class DebugURLsView(TemplateView):
    template_name = 'debug_urls.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resolver = get_resolver()
        context['urls'] = self.get_urls(resolver.url_patterns)
        return context
    
    def get_urls(self, urlpatterns, prefix=''):
        result = []
        for pattern in urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                # This is an include()
                result.extend(self.get_urls(pattern.url_patterns, prefix + str(pattern.pattern)))
            else:
                # This is a URL pattern
                try:
                    callback_str = f"{pattern.callback.__module__}.{pattern.callback.__name__}" if hasattr(pattern, 'callback') else 'No callback'
                except:
                    callback_str = 'Error getting callback'
                
                result.append({
                    'pattern': f"{prefix}{pattern.pattern}",
                    'name': pattern.name or 'No name',
                    'callback': callback_str,
                    'app_name': getattr(pattern, 'app_name', None),
                    'namespace': getattr(pattern, 'namespace', None),
                })
        return result


class TestAdminView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/unreademail/submission_list.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Test Admin View',
            'has_permission': self.request.user.is_staff,
            'site_header': 'Test Admin',
            'site_title': 'Test Admin',
            'site_url': '/',
            'is_popup': False,
            'is_nav_sidebar_enabled': False,
            'available_apps': [],
            'submissions': [],  # Empty for test
        })
        return context
