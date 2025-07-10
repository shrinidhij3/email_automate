#!/usr/bin/env python
"""
Test script to verify Django admin access and superuser credentials.
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

def test_admin_access():
    """Test admin panel access and superuser login."""
    print("=== Django Admin Access Test ===")
    
    # Check superusers
    superusers = User.objects.filter(is_superuser=True)
    print(f"Found {superusers.count()} superuser(s):")
    
    for user in superusers:
        print(f"  - {user.username} (ID: {user.id})")
        print(f"    Email: {user.email}")
        print(f"    Active: {user.is_active}")
        print(f"    Staff: {user.is_staff}")
        print(f"    Superuser: {user.is_superuser}")
        print()
    
    if not superusers.exists():
        print("❌ No superusers found!")
        return False
    
    # Test admin login with first superuser
    superuser = superusers.first()
    print(f"Testing admin login with superuser: {superuser.username}")
    
    client = Client()
    
    # Test admin index access (should redirect to login)
    print("\n1. Testing admin index access...")
    response = client.get('/admin/')
    print(f"   Status: {response.status_code}")
    print(f"   Redirected to: {response.url if hasattr(response, 'url') else 'No redirect'}")
    
    # Test admin login page
    print("\n2. Testing admin login page...")
    response = client.get('/admin/login/')
    print(f"   Status: {response.status_code}")
    print(f"   Content length: {len(response.content)}")
    
    # Test login with superuser credentials
    print(f"\n3. Testing login with superuser credentials...")
    login_data = {
        'username': superuser.username,
        'password': 'admin123',  # Try the default password
    }
    
    response = client.post('/admin/login/', login_data, follow=True)
    print(f"   Status: {response.status_code}")
    print(f"   Final URL: {response.redirect_chain[-1][0] if response.redirect_chain else 'No redirects'}")
    
    if response.status_code == 200 and '/admin/' in str(response.redirect_chain):
        print("✅ Admin login successful!")
        
        # Test admin index after login
        print("\n4. Testing admin index after login...")
        response = client.get('/admin/')
        print(f"   Status: {response.status_code}")
        print(f"   Content length: {len(response.content)}")
        
        if response.status_code == 200:
            print("✅ Admin panel accessible!")
            return True
        else:
            print("❌ Admin panel not accessible after login")
            return False
    else:
        print("❌ Admin login failed!")
        print("   Response content preview:", response.content[:200] if response.content else "No content")
        return False

def create_superuser():
    """Create a superuser if none exists."""
    print("\n=== Creating Superuser ===")
    
    if User.objects.filter(is_superuser=True).exists():
        print("Superuser already exists, skipping creation.")
        return
    
    try:
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print(f"✅ Created superuser: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Password: admin123")
    except Exception as e:
        print(f"❌ Failed to create superuser: {e}")

if __name__ == '__main__':
    print("Starting Django admin tests...")
    
    # Create superuser if needed
    create_superuser()
    
    # Test admin access
    success = test_admin_access()
    
    if success:
        print("\n🎉 All tests passed! Admin panel should be working.")
        print("\nYou can access the admin panel at: http://127.0.0.1:8000/admin/")
        print("Login with: admin / admin123")
    else:
        print("\n❌ Tests failed! Check the Django server logs for more details.")
    
    print("\n=== Test Complete ===") 