from django.db import migrations, models
import base64
from django.conf import settings
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def get_fernet_key():
    salt = settings.SECRET_KEY[:16].encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))

def encrypt_passwords(apps, schema_editor):
    UnreadEmail = apps.get_model('unread_emails', 'UnreadEmail')
    f = Fernet(get_fernet_key())
    
    for email in UnreadEmail.objects.all():
        if email.password:  # If there's an existing password
            encrypted = f.encrypt(email.password.encode())
            email._password = encrypted
            email.save(update_fields=['_password'])

class Migration(migrations.Migration):
    dependencies = [
        ('unread_emails', '0008_add_use_ssl_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='unreademail',
            name='_password',
            field=models.BinaryField(blank=True, null=True),
        ),
        migrations.RunPython(encrypt_passwords, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='unreademail',
            name='password',
        ),
        migrations.RenameField(
            model_name='unreademail',
            old_name='_password',
            new_name='password',
        ),
    ]
