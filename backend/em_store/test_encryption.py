import os
import django
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
try:
    django.setup()
    from unread_emails.models import UnreadEmail
    logger.info("Django setup completed successfully")
except Exception as e:
    logger.error(f"Error setting up Django: {e}")
    raise

def test_password_encryption():
    print("Testing password encryption...")
    
    # Create a test record
    test_password = "test_password_123"
    email = UnreadEmail(
        name="Test User",
        email="test@example.com",
        password=test_password,
        provider="gmail"
    )
    
    # Save the record (should trigger encryption)
    email.save()
    
    print(f"Original password: {test_password}")
    print(f"Encrypted password: {email.password}")
    
    # Test decryption
    decrypted = email.get_decrypted_password()
    print(f"Decrypted password: {decrypted}")
    
    # Verify
    if decrypted == test_password:
        print("✅ Password encryption and decryption works!")
    else:
        print("❌ Password encryption/decryption failed!")
    
    # Clean up
    email.delete()

if __name__ == "__main__":
    test_password_encryption()
