from django.db import migrations
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib

def get_fernet_key():
    # Generate a key from Django's SECRET_KEY
    secret = settings.SECRET_KEY.encode()
    key = hashlib.sha256(secret).digest()
    return base64.urlsafe_b64encode(key)

def encrypt_passwords(apps, schema_editor):
    UnreadEmail = apps.get_model('unread_emails', 'UnreadEmail')
    f = Fernet(get_fernet_key())
    
    for email in UnreadEmail.objects.all():
        if email.password and not email.password.startswith('gAA'):  # Simple check if not encrypted
            try:
                email.password = f.encrypt(email.password.encode()).decode()
                email.save(update_fields=['password'])
            except Exception as e:
                print(f"Error encrypting password for email {email.id}: {e}")

class Migration(migrations.Migration):
    dependencies = [
        ('unread_emails', '0012_encrypt_existing_passwords'),
    ]

    operations = [
        migrations.RunPython(encrypt_passwords, migrations.RunPython.noop),
    ]
