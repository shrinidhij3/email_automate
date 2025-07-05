from django.core.management.base import BaseCommand
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

class Command(BaseCommand):
    help = 'List all URLs in the project'

    def handle(self, *args, **options):
        self.print_urls(get_resolver().url_patterns)

    def print_urls(self, urlpatterns, prefix=''):
        for pattern in urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                # This is an include()
                self.print_urls(pattern.url_patterns, prefix + str(pattern.pattern))
            else:
                # This is a URL pattern
                self.stdout.write(f"{prefix}{pattern.pattern} -> {pattern.name or 'No name'}")
                if hasattr(pattern, 'lookup_str'):
                    self.stdout.write(f"    {pattern.lookup_str}")
                if hasattr(pattern, 'default_args'):
                    self.stdout.write(f"    {pattern.default_args}")
                if hasattr(pattern, 'app_name'):
                    self.stdout.write(f"    App: {pattern.app_name}")
                if hasattr(pattern, 'namespace'):
                    self.stdout.write(f"    Namespace: {pattern.namespace}")
