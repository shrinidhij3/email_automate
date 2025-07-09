from rest_framework import serializers
from .models import EmailCampaign, CampaignEmailAttachment

class CampaignEmailAttachmentSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CampaignEmailAttachment
        fields = [
            'id', 'file', 'original_filename', 'content_type', 
            'file_size', 'download_url', 'created_at'
        ]
        read_only_fields = [
            'id', 'original_filename', 'content_type', 
            'file_size', 'download_url', 'created_at'
        ]
        extra_kwargs = {
            'file': {'write_only': True}
        }
    
    def get_download_url(self, obj):
        """Return the download URL for the file."""
        return obj.get_download_url()

class EmailCampaignSerializer(serializers.ModelSerializer):
    attachments = CampaignEmailAttachmentSerializer(many=True, read_only=True)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    
    subject = serializers.CharField(required=False, allow_blank=True, default='')
    body = serializers.CharField(required=False, allow_blank=True, default='')
    
    class Meta:
        model = EmailCampaign
        fields = [
            'id', 'name', 'subject', 'body', 'created_by', 'email', 'password',
            'provider', 'imap_host', 'imap_port', 'smtp_host', 'smtp_port',
            'use_ssl', 'notes', 'attachments', 'uploaded_files'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'created_by': {'required': False}
        }
    
    def create(self, validated_data):
        uploaded_files = validated_data.pop('uploaded_files', [])
        request = self.context.get('request')
        
        # Set the created_by user if not already set
        if request and request.user.is_authenticated:
            if 'created_by' not in validated_data:
                validated_data['created_by'] = request.user
        
        # Create the campaign first
        campaign = EmailCampaign.objects.create(**validated_data)
        
        # Process each uploaded file
        for file in uploaded_files:
            try:
                # Get file metadata safely
                original_filename = getattr(file, 'name', 'unnamed_file')
                content_type = getattr(file, 'content_type', 'application/octet-stream')
                
                # Create the attachment - let the model handle the R2 upload
                CampaignEmailAttachment.objects.create(
                    email_campaign=campaign,
                    file=file,
                    original_filename=original_filename,
                    content_type=content_type,
                    # file_size will be set by the model
                )
            except Exception as e:
                # Log the error but don't fail the entire request
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error processing file {getattr(file, 'name', 'unknown')}: {str(e)}", exc_info=True)
                # Optionally, you could collect these errors and include them in the response
                
        return campaign
        
    def update(self, instance, validated_data):
        # Handle file updates if provided
        file = validated_data.pop('file', None)
        if file:
            # Delete the old file from R2
            if instance.file:
                instance.file.delete(save=False)
                
            # Update file-related fields
            instance.file = file
            instance.original_filename = getattr(file, 'name', 'unnamed_file')
            instance.content_type = getattr(file, 'content_type', 'application/octet-stream')
            
            # Clear the download URL so it gets regenerated
            instance.download_url = None
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance
