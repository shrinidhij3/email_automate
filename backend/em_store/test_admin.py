#!/usr/bin/env python
"""
Test script to verify Django admin access
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

def test_admin_access():
    """Test Django admin access"""
    print("Testing Django admin access...")
    
    # Create a test client
    client = Client()
    
    # Test admin login page
    try:
        response = client.get('/admin/')
        print(f"Admin page status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Admin page accessible")
        else:
            print(f"❌ Admin page returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing admin: {e}")
    
    # Test if we can create a superuser
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print("✅ Superuser created successfully")
        else:
            print("✅ Superuser already exists")
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

if __name__ == '__main__':
    test_admin_access() 