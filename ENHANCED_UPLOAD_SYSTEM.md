# Enhanced Upload System Documentation

## Overview

This document describes the enhanced file upload system that automatically extracts and stores public URLs from Cloudflare R2 for both unread emails and campaigns. The system provides robust error handling, comprehensive logging, and multiple URL generation strategies.

## Key Features

### 1. Enhanced URL Generation
- **Multiple URL Strategies**: The system uses multiple strategies to generate public URLs
- **Custom Domain Support**: Supports custom domains for better SSL compatibility
- **Fallback Mechanisms**: Multiple fallback options if primary URL generation fails
- **Account ID Extraction**: Automatically extracts account ID from R2 endpoint URLs

### 2. Comprehensive Error Handling
- **Upload Failures**: Graceful handling of upload failures with detailed error messages
- **URL Generation Issues**: Fallback mechanisms for URL generation problems
- **Database Errors**: Proper error handling for database operations
- **Network Issues**: Timeout handling for URL accessibility tests

### 3. Enhanced Logging
- **Detailed Logging**: Comprehensive logging for debugging and monitoring
- **Upload Tracking**: Track successful and failed uploads
- **URL Generation Logging**: Log URL generation attempts and results
- **Error Tracking**: Detailed error logging with stack traces

## System Architecture

### Storage Utilities (`em_store/storage_utils.py`)

#### Core Functions

1. **`upload_file_to_r2(file_obj, file_name, content_type, folder)`**
   - Uploads files to Cloudflare R2
   - Generates public URLs automatically
   - Returns comprehensive result object

2. **`generate_public_url(file_key)`**
   - Uses multiple strategies to generate public URLs
   - Supports custom domains and R2 public URLs
   - Provides fallback mechanisms

3. **`validate_r2_configuration()`**
   - Validates R2 configuration settings
   - Checks required and optional settings
   - Tests storage backend connectivity

#### URL Generation Strategies

1. **Custom Domain Strategy**
   ```python
   url = f"https://{custom_domain}/{file_key}"
   ```

2. **R2 Public URL Strategy**
   ```python
   url = f"https://{account_id}.r2.cloudflarestorage.com/{bucket_name}/{file_key}"
   ```

3. **Default Storage Strategy**
   ```python
   url = default_storage.url(file_key)
   ```

### Model Enhancements

#### UnreadEmailAttachment Model

- **Enhanced `save()` method**: Automatically uploads to R2 and generates URLs
- **Improved `get_download_url()`**: Generates URLs on-demand if not stored
- **Better `_generate_download_url()`**: Uses enhanced storage utilities

#### CampaignEmailAttachment Model

- **Enhanced `save()` method**: Automatically uploads to R2 and generates URLs
- **Improved `get_download_url()`**: Generates URLs on-demand if not stored
- **Better `_generate_download_url()`**: Uses enhanced storage utilities

### View Enhancements

#### Unread Emails Views

- **Fixed file handling**: Proper file field assignment before saving
- **Enhanced error handling**: Better error messages and logging
- **URL generation**: Automatic URL generation and storage

#### Campaigns Views

- **Fixed file handling**: Proper file field assignment before saving
- **Enhanced error handling**: Better error messages and logging
- **URL generation**: Automatic URL generation and storage

## Configuration Requirements

### Environment Variables

```bash
# Required
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=email-autoamation
R2_ENDPOINT_URL=https://4d4c294f4e40b9cb08edf870ed60b046.r2.cloudflarestorage.com

# Optional (for better SSL compatibility)
R2_CUSTOM_DOMAIN=email-autoamation.r2.cloudflarestorage.com
```

### Django Settings

```python
# Cloudflare R2 Configuration
AWS_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('R2_BUCKET_NAME', 'email-autoamation')
AWS_S3_ENDPOINT_URL = os.getenv('R2_ENDPOINT_URL', 'https://4d4c294f4e40b9cb08edf870ed60b046.r2.cloudflarestorage.com')
AWS_S3_CUSTOM_DOMAIN = os.getenv('R2_CUSTOM_DOMAIN', f'{AWS_STORAGE_BUCKET_NAME}.r2.cloudflarestorage.com')
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_S3_VERIFY = True
AWS_S3_REGION_NAME = 'auto'
```

## Frontend Integration

### Unread Emails Form

The frontend sends files as `files` field in FormData:

```javascript
const formDataToSend = new FormData();
formDataToSend.append('name', formData.name);
formDataToSend.append('email', formData.email);
formDataToSend.append('password', formData.password);
// ... other fields ...

// Add files to FormData
if (formData.files) {
  Array.from(formData.files).forEach((file) => {
    formDataToSend.append('files', file);
  });
}
```

### Campaigns Form

The frontend sends files as `uploaded_files` field in FormData:

```javascript
const form = new FormData();
form.append('name', formData.name.trim());
form.append('email', formData.email.trim());
form.append('password', formData.password);
// ... other fields ...

formData.files.forEach((file, index) => {
  form.append('uploaded_files', file);
});
```

## File Upload Flow

### 1. Frontend Submission
- User selects files and submits form
- Files are sent as FormData with appropriate field names
- Content-Type is set to `multipart/form-data`

### 2. Backend Processing
- Request is received by the appropriate ViewSet
- Form data is validated using serializers
- Campaign/UnreadEmail record is created

### 3. File Processing
- Files are extracted from `request.FILES`
- Each file is validated for size and type
- Attachment objects are created with file metadata

### 4. R2 Upload
- File content is read and uploaded to R2
- Multiple URL generation strategies are attempted
- Best available URL is selected and stored

### 5. Database Storage
- Attachment record is saved with R2 key and URL
- File metadata is stored (size, content type, etc.)
- Download URL is stored in `download_url` field

## Error Handling

### Upload Failures
```python
if upload_result['success']:
    # Store URL and continue
    self.download_url = upload_result['url']
else:
    # Log error and raise exception
    logger.error(f"Failed to upload file to R2: {upload_result.get('error')}")
    raise Exception(f"Failed to upload file to storage: {upload_result.get('error')}")
```

### URL Generation Failures
```python
try:
    url = generate_public_url(file_key)
    return url
except Exception as e:
    logger.error(f"Error generating public URL: {str(e)}", exc_info=True)
    # Return fallback URL
    return f"https://{bucket_name}.r2.cloudflarestorage.com/{file_key}"
```

### Database Errors
```python
try:
    attachment.save()
except Exception as e:
    logger.error(f"Error saving attachment: {str(e)}", exc_info=True)
    # Handle database errors gracefully
```

## Testing

### Test Scripts

1. **`test_enhanced_uploads.py`**: Comprehensive test for both systems
2. **`test_fixes.py`**: Basic functionality tests
3. **`test_ssl_urls.py`**: SSL URL generation tests

### Running Tests

```bash
cd backend/em_store
python test_enhanced_uploads.py
```

### Test Coverage

- R2 configuration validation
- Storage utilities functionality
- Unread email attachment uploads
- Campaign attachment uploads
- Database storage verification
- URL accessibility testing
- Error handling verification

## Monitoring and Logging

### Log Levels

- **INFO**: Successful operations, URL generation
- **WARNING**: Non-critical issues, fallback usage
- **ERROR**: Upload failures, URL generation errors
- **DEBUG**: Detailed debugging information

### Key Log Messages

```python
logger.info(f"Successfully uploaded file to R2: {upload_result['key']}")
logger.info(f"Generated download URL: {upload_result['url']}")
logger.info(f"Updated attachment {self.pk} with download URL: {self.download_url}")
logger.error(f"Failed to upload file to R2: {upload_result.get('error')}")
logger.warning(f"No file associated with attachment {self.pk}")
```

## Troubleshooting

### Common Issues

1. **SSL/TLS Protocol Mismatch**
   - Ensure custom domain is properly configured
   - Check SSL certificate validity
   - Use R2 public URLs as fallback

2. **Upload Failures**
   - Verify R2 credentials
   - Check bucket permissions
   - Validate file size limits

3. **URL Generation Issues**
   - Check custom domain configuration
   - Verify account ID extraction
   - Test fallback URL generation

### Debugging Steps

1. **Check Configuration**
   ```python
   from em_store.storage_utils import validate_r2_configuration
   config_status = validate_r2_configuration()
   print(config_status)
   ```

2. **Test URL Generation**
   ```python
   from em_store.storage_utils import generate_public_url
   url = generate_public_url('test/file.txt')
   print(url)
   ```

3. **Check Logs**
   - Review Django logs for error messages
   - Check R2 access logs
   - Monitor URL accessibility

## Performance Considerations

### File Size Limits
- Maximum file size: 10MB per file
- Configurable in settings
- Validated before upload

### URL Generation Performance
- Multiple strategies with fallbacks
- Caching of generated URLs
- Lazy URL generation on demand

### Database Optimization
- Efficient queries for attachment retrieval
- Proper indexing on file fields
- Batch operations for multiple files

## Security Considerations

### File Validation
- Content type validation
- File size limits
- Malicious file detection

### Access Control
- User-based permissions
- Campaign ownership validation
- Secure URL generation

### Data Protection
- Encrypted password storage
- Secure file uploads
- Protected download URLs

## Future Enhancements

### Planned Features
- Pre-signed URL generation
- File compression
- Image optimization
- CDN integration
- Advanced file validation
- Bulk upload optimization

### Monitoring Improvements
- Upload success rate tracking
- URL accessibility monitoring
- Performance metrics
- Error rate analysis 