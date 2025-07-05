import os
import django
import requests
from django.core.files.uploadedfile import SimpleUploadedFile

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from campaigns.models import Campaign, CampaignEmailAttachment

def test_campaign_attachment_upload():
    """Test uploading a file to a campaign"""
    print("\n=== Testing Campaign File Upload ===\n")
    
    # Create a test campaign
    campaign = Campaign.objects.create(
        name="Test Campaign",
        subject="Test Subject",
        body="Test Body",
        status="draft"
    )
    
    print(f"Created test campaign with ID: {campaign.id}")
    
    # Create a test file
    test_file_path = "test_upload.txt"
    with open(test_file_path, 'w') as f:
        f.write("This is a test file for upload.")
    
    # Create a file for upload
    with open(test_file_path, 'rb') as f:
        file_content = f.read()
    
    upload_file = SimpleUploadedFile(
        name="test_upload.txt",
        content=file_content,
        content_type="text/plain"
    )
    
    # Create an attachment
    attachment = CampaignEmailAttachment(
        campaign=campaign,
        file=upload_file,
        original_filename="test_upload.txt",
        content_type="text/plain",
        file_size=len(file_content)
    )
    attachment.save()
    
    print(f"Created attachment with ID: {attachment.id}")
    print(f"File path: {attachment.file.path}")
    print(f"File URL: {attachment.file.url if hasattr(attachment.file, 'url') else 'N/A'}")
    print(f"Download URL: {attachment.download_url or 'N/A'}")
    
    # Clean up
    os.remove(test_file_path)
    
    return attachment

if __name__ == "__main__":
    attachment = test_campaign_attachment_upload()
    print("\nTest completed successfully!")
    print(f"You can find the test attachment at: {attachment.file.path}")
import requests
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000/"  # Update if your backend is running on a different URL
API_TOKEN = ""  # Add your API token if authentication is required

# Test file paths - you can add more test files here
TEST_FILES = [
    "test.txt",
    "test.jpg",
    "test.pdf"
]

def create_test_file(filename, size_kb=10):
    """Create a test file with the given size in KB"""
    filepath = Path(filename)
    if not filepath.exists():
        with open(filepath, 'wb') as f:
            f.write(os.urandom(1024 * size_kb))  # Create a file of size_kb KB
    return filepath

def test_file_upload(file_path):
    """Test uploading a file to the unread emails endpoint"""
    url = f"{BASE_URL}api/unread-emails/submissions/"
    
    # Prepare the form data
    data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'testpassword',
        'provider': 'gmail',
        'imap_host': 'imap.gmail.com',
        'imap_port': '993',
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': '587',
        'secure': 'true',
        'use_ssl': 'true',
        'notes': 'Test file upload',
        'is_processed': 'false'
    }
    
    # Prepare the file for upload
    with open(file_path, 'rb') as f:
        files = {
            'files': (os.path.basename(file_path), f, 'application/octet-stream')
        }
        
        # Set up headers
        headers = {}
        if API_TOKEN:
            headers['Authorization'] = f"Token {API_TOKEN}"
        
        # Make the request
        print(f"\nUploading file: {file_path}")
        response = requests.post(
            url,
            data=data,
            files=files,
            headers=headers
        )
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        print("✅ Success! File uploaded successfully.")
        print("Response:", response.json())
    else:
        print("❌ Failed to upload file.")
        print("Response:", response.text)
    
    return response

def main():
    print("=== Testing File Upload to Cloudflare R2 ===\n")
    
    # Create test files if they don't exist
    for filename in TEST_FILES:
        create_test_file(filename)
    
    # Test uploading each file
    for filename in TEST_FILES:
        if os.path.exists(filename):
            test_file_upload(filename)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
