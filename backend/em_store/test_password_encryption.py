import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from unread_emails.models import UnreadEmail
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib

def get_fernet_key():
    # Generate a key from Django's SECRET_KEY
    secret = settings.SECRET_KEY.encode()
    key = hashlib.sha256(secret).digest()
    return base64.urlsafe_b64encode(key)

def test_encryption():
    print("Testing password encryption...")
    
    # Test data
    test_password = "test_password_123"
    
    # Create a test record
    try:
        print("Creating test record...")
        email = UnreadEmail.objects.create(
            name="Test User",
            email="test@example.com",
            password=test_password,
            provider="gmail",
            imap_host="imap.gmail.com",
            imap_port=993,
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            secure=True,
            use_ssl=True,
            notes="Test record for password encryption"
        )
        
        # Check if password was encrypted
        print("\nChecking password encryption...")
        print(f"Original password: {test_password}")
        print(f"Stored password: {email.password}")
        
        if email.password == test_password:
            print("❌ ERROR: Password was not encrypted!")
        elif not email.password.startswith('gAA'):
            print("❌ WARNING: Password doesn't look like a Fernet token")
        else:
            print("✅ Password appears to be encrypted")
            
            # Test decryption
            try:
                decrypted = email.get_decrypted_password()
                print(f"Decrypted password: {decrypted}")
                if decrypted == test_password:
                    print("✅ Decryption successful!")
                else:
                    print("❌ Decryption failed: Incorrect password")
            except Exception as e:
                print(f"❌ Error during decryption: {e}")
        
        # Clean up
        print("\nCleaning up test record...")
        email.delete()
        print("✅ Test complete")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        raise

if __name__ == "__main__":
    test_encryption()
