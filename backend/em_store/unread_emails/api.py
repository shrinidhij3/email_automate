from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import UnreadEmail

@csrf_exempt
@require_http_methods(["POST"])
def save_email_config(request):
    try:
        data = json.loads(request.body) if request.body else {}
        
        email = data.get("email")
        password = data.get("password")
        provider = data.get("provider")

        if not all([email, password, provider]):
            return JsonResponse({"error": "Email, password, and provider are required"}, status=400)

        # Default config (will be used for 'other' provider if no values provided)
        imap_host = data.get("imap_host")
        imap_port = data.get("imap_port")
        smtp_host = data.get("smtp_host")
        smtp_port = data.get("smtp_port")
        secure = data.get("secure", True)

        known_providers = {
            "gmail": {
                "imap_host": "imap.gmail.com",
                "imap_port": 993,
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "secure": True
            }
        }

        if provider in known_providers:
            config = known_providers[provider]
            imap_host = config["imap_host"]
            imap_port = config["imap_port"]
            smtp_host = config["smtp_host"]
            smtp_port = config["smtp_port"]
            secure = config["secure"]
        elif not all([imap_host, imap_port, smtp_host, smtp_port]):
            return JsonResponse(
                {"error": "Missing IMAP/SMTP configuration for custom provider"}, 
                status=400
            )

        # Create or update the email configuration
        use_ssl = data.get('use_ssl', secure)  # Default to secure if use_ssl not provided
        defaults = {
            'name': data.get('name', email.split('@')[0]),
            'password': password,
            'provider': provider,
            'imap_host': imap_host,
            'imap_port': imap_port,
            'smtp_host': smtp_host,
            'smtp_port': smtp_port,
            'secure': secure,
            'use_ssl': use_ssl,  # Set use_ssl from request or default to secure
            'notes': data.get('notes')
        }
        
        # Ensure both fields are set to the same value if one is missing
        if 'secure' not in data and 'use_ssl' in data:
            defaults['secure'] = use_ssl
        elif 'use_ssl' not in data and 'secure' in data:
            defaults['use_ssl'] = secure
            
        UnreadEmail.objects.update_or_create(
            email=email,
            defaults=defaults
        )

        return JsonResponse({"status": "success"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
