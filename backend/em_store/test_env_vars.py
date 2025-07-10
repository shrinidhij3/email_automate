#!/usr/bin/env python
"""
Test script to verify environment variables are loaded correctly
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from django.conf import settings

def test_environment_variables():
    """Test if environment variables are loaded correctly"""
    print("=== Testing Environment Variables ===")
    
    # Check raw environment variables
    print("\n1. Raw environment variables:")
    print(f"R2_ACCESS_KEY_ID: {os.getenv('R2_ACCESS_KEY_ID', 'Not set')}")
    print(f"R2_SECRET_ACCESS_KEY: {'Set' if os.getenv('R2_SECRET_ACCESS_KEY') else 'Not set'}")
    print(f"R2_BUCKET_NAME: {os.getenv('R2_BUCKET_NAME', 'Not set')}")
    print(f"R2_ENDPOINT_URL: {os.getenv('R2_ENDPOINT_URL', 'Not set')}")
    
    # Check Django settings
    print("\n2. Django settings:")
    print(f"AWS_ACCESS_KEY_ID: {getattr(settings, 'AWS_ACCESS_KEY_ID', 'Not set')}")
    print(f"AWS_SECRET_ACCESS_KEY: {'Set' if getattr(settings, 'AWS_SECRET_ACCESS_KEY', None) else 'Not set'}")
    print(f"AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")
    print(f"AWS_S3_ENDPOINT_URL: {getattr(settings, 'AWS_S3_ENDPOINT_URL', 'Not set')}")
    print(f"AWS_S3_CUSTOM_DOMAIN: {getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', 'Not set')}")
    
    # Check storage configuration
    print("\n3. Storage configuration:")
    print(f"STORAGES: {getattr(settings, 'STORAGES', 'Not set')}")
    
    # Test if we can import storage backends
    print("\n4. Testing storage backends:")
    try:
        from em_store.storage_backends import R2MediaStorage
        storage = R2MediaStorage()
        print(f"✅ R2MediaStorage created successfully")
        print(f"   Bucket: {storage.bucket_name}")
        print(f"   Endpoint: {storage.endpoint_url}")
        print(f"   Custom domain: {storage.custom_domain}")
    except Exception as e:
        print(f"❌ Error creating R2MediaStorage: {e}")

if __name__ == '__main__':
    test_environment_variables() 