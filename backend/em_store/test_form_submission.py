import os
import sys
import django
import requests
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from unread_emails.models import UnreadEmail

def test_form_submission():
    print("Testing form submission and password encryption...")
    
    # Test data
    test_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'test_password_123',
        'provider': 'gmail',
        'imap_host': 'imap.gmail.com',
        'imap_port': '993',
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': '587',
        'secure': 'true',
        'use_ssl': 'true',
        'notes': 'Test submission',
    }
    
    # Get CSRF token first
    try:
        print("\n1. Getting CSRF token...")
        session = requests.Session()
        response = session.get('http://localhost:8000/api/csrf/')
        csrf_token = response.json().get('csrfToken')
        print(f"CSRF Token: {csrf_token}")
        
        # Submit the form
        print("\n2. Submitting form...")
        response = session.post(
            'http://localhost:8000/api/unread-emails/submissions/',
            data=test_data,
            headers={
                'X-CSRFToken': csrf_token,
                'Referer': 'http://localhost:8000'
            }
        )
        
        if response.status_code == 201:
            print("✅ Form submitted successfully!")
            result = response.json()
            email_id = result.get('id')
            print(f"Created email record with ID: {email_id}")
            
            # Check the database
            print("\n3. Checking database...")
            try:
                email = UnreadEmail.objects.get(id=email_id)
                print(f"Found email record: {email.email}")
                print(f"Stored password: {email.password}")
                
                if email.password == test_data['password']:
                    print("❌ ERROR: Password was not encrypted!")
                elif not email.password.startswith('gAA'):
                    print("❌ WARNING: Password doesn't look like a Fernet token")
                else:
                    print("✅ Password appears to be encrypted")
                    
                    # Test decryption
                    try:
                        decrypted = email.get_decrypted_password()
                        print(f"Decrypted password: {decrypted}")
                        if decrypted == test_data['password']:
                            print("✅ Decryption successful!")
                        else:
                            print("❌ Decryption failed: Incorrect password")
                    except Exception as e:
                        print(f"❌ Error during decryption: {e}")
                
                # Clean up
                print("\n4. Cleaning up test record...")
                email.delete()
                print("✅ Test record deleted")
                
            except UnreadEmail.DoesNotExist:
                print("❌ ERROR: Could not find the created email record")
            except Exception as e:
                print(f"❌ ERROR: {e}")
                
        else:
            print(f"❌ Form submission failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_form_submission()
