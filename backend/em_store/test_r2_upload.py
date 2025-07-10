#!/usr/bin/env python
"""
Test script to verify R2 file upload functionality
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
from em_store.storage_utils import upload_file_to_r2, delete_file_from_r2

def test_r2_configuration():
    """Test R2 configuration and upload"""
    print("=== Testing R2 Configuration ===")
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    print(f"R2_ACCESS_KEY_ID: {'Set' if os.getenv('R2_ACCESS_KEY_ID') else 'Not set'}")
    print(f"R2_SECRET_ACCESS_KEY: {'Set' if os.getenv('R2_SECRET_ACCESS_KEY') else 'Not set'}")
    print(f"R2_BUCKET_NAME: {os.getenv('R2_BUCKET_NAME', 'Not set')}")
    print(f"R2_ENDPOINT_URL: {os.getenv('R2_ENDPOINT_URL', 'Not set')}")
    
    # Check Django settings
    print("\n2. Checking Django settings...")
    print(f"AWS_ACCESS_KEY_ID: {'Set' if getattr(settings, 'AWS_ACCESS_KEY_ID', None) else 'Not set'}")
    print(f"AWS_SECRET_ACCESS_KEY: {'Set' if getattr(settings, 'AWS_SECRET_ACCESS_KEY', None) else 'Not set'}")
    print(f"AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")
    print(f"AWS_S3_ENDPOINT_URL: {getattr(settings, 'AWS_S3_ENDPOINT_URL', 'Not set')}")
    print(f"AWS_S3_CUSTOM_DOMAIN: {getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', 'Not set')}")
    
    # Test file upload
    print("\n3. Testing file upload...")
    try:
        # Create a test file
        test_content = b"This is a test file for R2 upload verification."
        test_filename = "test_upload.txt"
        
        print(f"Uploading test file: {test_filename}")
        result = upload_file_to_r2(
            test_content,
            file_name=test_filename,
            content_type='text/plain',
            folder='test_uploads'
        )
        
        if result['success']:
            print(f"✅ Upload successful!")
            print(f"   URL: {result['url']}")
            print(f"   Key: {result['key']}")
            
            # Test file deletion
            print(f"\n4. Testing file deletion...")
            delete_result = delete_file_from_r2(result['key'])
            if delete_result:
                print(f"✅ File deletion successful!")
            else:
                print(f"❌ File deletion failed!")
        else:
            print(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_r2_configuration() 