import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from unread_emails.models import UnreadEmail, UnreadEmailAttachment

def test_attachment_creation():
    """Test creating a new attachment with the updated model"""
    print("\n=== Testing UnreadEmailAttachment Model ===\n")
    
    # Create a test unread email
    unread_email = UnreadEmail.objects.create(
        name="Test User",
        email="test@example.com",
        password="testpassword",
        provider="gmail",
        imap_host="imap.gmail.com",
        imap_port=993,
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        secure=True,
        use_ssl=True,
        notes="Test attachment"
    )
    
    print(f"Created test unread email with ID: {unread_email.id}")
    
    # Create a test file
    test_file_path = "test_attachment.txt"
    with open(test_file_path, 'w') as f:
        f.write("This is a test attachment file.")
    
    # Create an attachment
    with open(test_file_path, 'rb') as f:
        attachment = UnreadEmailAttachment(
            unread_email=unread_email,
            original_filename="test_attachment.txt",
            content_type="text/plain",
            file_size=os.path.getsize(test_file_path)
        )
        attachment.file.save("test_attachment.txt", f, save=False)
        attachment.save()
    
    print(f"Created attachment with ID: {attachment.id}")
    print(f"File path: {attachment.file.path}")
    print(f"File URL: {attachment.file.url if hasattr(attachment.file, 'url') else 'N/A'}")
    print(f"Download URL: {attachment.download_url or 'N/A'}")
    
    # Clean up
    os.remove(test_file_path)
    
    return attachment

if __name__ == "__main__":
    attachment = test_attachment_creation()
    print("\nTest completed successfully!")
    print(f"You can find the test attachment at: {attachment.file.path}")
