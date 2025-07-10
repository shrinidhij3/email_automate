#!/usr/bin/env python
"""
Test to list available R2 buckets and check account configuration
"""
import os
import sys
import django
import boto3
from botocore.exceptions import ClientError

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from django.conf import settings

def test_list_buckets():
    """Test listing buckets and account configuration"""
    print("=== Testing R2 Account and Buckets ===")
    
    # Check all settings
    print("\n1. Checking settings:")
    print(f"AWS_ACCESS_KEY_ID: {settings.AWS_ACCESS_KEY_ID}")
    print(f"AWS_SECRET_ACCESS_KEY: {'Set' if settings.AWS_SECRET_ACCESS_KEY else 'Not set'}")
    print(f"AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}")
    
    # Check if any required values are None
    if not settings.AWS_ACCESS_KEY_ID:
        print("❌ AWS_ACCESS_KEY_ID is None or empty")
        return
    if not settings.AWS_SECRET_ACCESS_KEY:
        print("❌ AWS_SECRET_ACCESS_KEY is None or empty")
        return
    if not settings.AWS_STORAGE_BUCKET_NAME:
        print("❌ AWS_STORAGE_BUCKET_NAME is None or empty")
        return
    if not settings.AWS_S3_ENDPOINT_URL:
        print("❌ AWS_S3_ENDPOINT_URL is None or empty")
        return
    
    try:
        # Create S3 client for R2
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name='auto'
        )
        
        print(f"\n✅ S3 client created successfully")
        print(f"   Access Key ID: {settings.AWS_ACCESS_KEY_ID[:10]}...")
        print(f"   Endpoint: {settings.AWS_S3_ENDPOINT_URL}")
        
        # List buckets
        print(f"\n📋 Listing buckets...")
        try:
            response = s3_client.list_buckets()
            buckets = response.get('Buckets', [])
            
            if buckets:
                print(f"✅ Found {len(buckets)} bucket(s):")
                for bucket in buckets:
                    print(f"   - {bucket['Name']} (created: {bucket['CreationDate']})")
                    
                    # Check if this is our target bucket
                    if bucket['Name'] == settings.AWS_STORAGE_BUCKET_NAME:
                        print(f"     ✅ This is our target bucket!")
                    else:
                        print(f"     ❌ Not our target bucket")
            else:
                print(f"❌ No buckets found")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f"❌ Error listing buckets: {error_code}")
            print(f"   Error message: {e.response['Error']['Message']}")
            
            if error_code == '403':
                print(f"   This suggests a permissions issue with the API token")
            elif error_code == '522':
                print(f"   This suggests a connection issue or incorrect endpoint")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_list_buckets() 