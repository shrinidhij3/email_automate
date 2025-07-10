#!/usr/bin/env python
"""
Test script to verify Django admin access and configuration
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

# Import Django modules after setup
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

def test_admin_access():
    """Test admin panel access"""
    print("=== Testing Django Admin Access ===")
    
    # Test 1: Check if superusers exist
    print("\n1. Checking for superusers...")
    superusers = User.objects.filter(is_superuser=True)
    if superusers.exists():
        print(f"✓ Found {superusers.count()} superuser(s):")
        for user in superusers:
            print(f"  - {user.username} (email: {user.email})")
    else:
        print("✗ No superusers found!")
        return False
    
    # Test 2: Test admin login
    print("\n2. Testing admin login...")
    client = Client()
    
    # Try to access admin login page
    try:
        response = client.get('/admin/')
        print(f"✓ Admin login page accessible: {response.status_code}")
    except Exception as e:
        print(f"✗ Error accessing admin login page: {e}")
        return False
    
    # Test 3: Test authentication
    print("\n3. Testing authentication...")
    for user in superusers:
        print(f"Testing login for user: {user.username}")
        
        # Try to authenticate
        authenticated_user = authenticate(username=user.username, password='admin123')
        if authenticated_user:
            print(f"✓ Authentication successful for {user.username}")
        else:
            print(f"✗ Authentication failed for {user.username}")
            
        # Try to login via admin
        login_success = client.login(username=user.username, password='admin123')
        if login_success:
            print(f"✓ Admin login successful for {user.username}")
            
            # Try to access admin index
            response = client.get('/admin/')
            if response.status_code == 200:
                print(f"✓ Admin index accessible after login: {response.status_code}")
            else:
                print(f"✗ Admin index not accessible after login: {response.status_code}")
        else:
            print(f"✗ Admin login failed for {user.username}")
    
    # Test 4: Check CSRF configuration
    print("\n4. Checking CSRF configuration...")
    try:
        from em_store.middleware import CSRFMiddleware
        print("✓ Custom CSRF middleware found")
    except ImportError:
        print("✗ Custom CSRF middleware not found")
    
    # Test 5: Check static files configuration
    print("\n5. Checking static files configuration...")
    print(f"STATIC_URL: {getattr(settings, 'STATIC_URL', 'Not set')}")
    print(f"STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'Not set')}")
    print(f"STORAGES: {getattr(settings, 'STORAGES', 'Not set')}")
    
    # Test 6: Check R2 configuration
    print("\n6. Checking R2 configuration...")
    print(f"AWS_ACCESS_KEY_ID: {'Set' if getattr(settings, 'AWS_ACCESS_KEY_ID', None) else 'Not set'}")
    print(f"AWS_SECRET_ACCESS_KEY: {'Set' if getattr(settings, 'AWS_SECRET_ACCESS_KEY', None) else 'Not set'}")
    print(f"AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")
    print(f"AWS_S3_ENDPOINT_URL: {getattr(settings, 'AWS_S3_ENDPOINT_URL', 'Not set')}")
    
    return True

def test_file_upload_config():
    """Test file upload configuration"""
    print("\n=== Testing File Upload Configuration ===")
    
    # Test 1: Check storage backends
    print("\n1. Checking storage backends...")
    try:
        from em_store.storage_backends import R2MediaStorage
        print("✓ R2MediaStorage found")
    except ImportError as e:
        print(f"✗ R2MediaStorage not found: {e}")
    
    # Test 2: Check storage utilities
    print("\n2. Checking storage utilities...")
    try:
        from em_store.storage_utils import upload_file_to_r2, delete_file_from_r2
        print("✓ Storage utilities found")
    except ImportError as e:
        print(f"✗ Storage utilities not found: {e}")
    
    # Test 3: Check models
    print("\n3. Checking models...")
    try:
        from campaigns.models import CampaignEmailAttachment
        from unread_emails.models import UnreadEmailAttachment
        print("✓ Attachment models found")
    except ImportError as e:
        print(f"✗ Attachment models not found: {e}")

if __name__ == '__main__':
    print("Starting Django Admin and File Upload Tests...")
    
    success = test_admin_access()
    test_file_upload_config()
    
    if success:
        print("\n=== Tests completed successfully ===")
    else:
        print("\n=== Tests completed with errors ===")
        sys.exit(1) 