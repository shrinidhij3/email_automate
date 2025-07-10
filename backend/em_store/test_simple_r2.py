#!/usr/bin/env python
"""
Simple R2 upload test that bypasses the exists check
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

def test_direct_r2_upload():
    """Test direct upload to R2 using boto3"""
    print("=== Testing Direct R2 Upload ===")
    
    try:
        # Create S3 client for R2
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name='auto'  # R2 doesn't use regions like S3
        )
        
        print(f"✅ S3 client created successfully")
        print(f"   Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
        print(f"   Endpoint: {settings.AWS_S3_ENDPOINT_URL}")
        
        # Test bucket access
        try:
            response = s3_client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
            print(f"✅ Bucket access successful")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ Bucket not found: {settings.AWS_STORAGE_BUCKET_NAME}")
                return
            elif error_code == '403':
                print(f"❌ Access denied to bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
                return
            else:
                print(f"❌ Bucket access error: {error_code}")
                return
        
        # Test file upload
        test_content = b"This is a test file for direct R2 upload."
        test_key = "test_uploads/direct_test.txt"
        
        print(f"\n📤 Uploading test file: {test_key}")
        
        response = s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain',
            ACL='public-read'
        )
        
        print(f"✅ Direct upload successful!")
        print(f"   ETag: {response['ETag']}")
        print(f"   URL: https://{settings.AWS_S3_CUSTOM_DOMAIN}/{test_key}")
        
        # Test file deletion
        print(f"\n🗑️ Testing file deletion...")
        delete_response = s3_client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=test_key
        )
        print(f"✅ File deletion successful!")
        
    except Exception as e:
        print(f"❌ Direct upload test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_direct_r2_upload() 