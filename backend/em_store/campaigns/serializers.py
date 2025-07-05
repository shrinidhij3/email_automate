from rest_framework import serializers
from .models import EmailCampaign, CampaignEmailAttachment

class CampaignEmailAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignEmailAttachment
        fields = ['id', 'file', 'original_filename', 'content_type', 'file_size']
        read_only_fields = ['id', 'original_filename', 'content_type', 'file_size']

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
        
        # Create the campaign first
        campaign = EmailCampaign.objects.create(**validated_data)
        
        # Process each uploaded file
        for file in uploaded_files:
            try:
                # Get file metadata safely
                original_filename = getattr(file, 'name', 'unnamed_file')
                
                # Create the attachment - let the model handle the rest
                CampaignEmailAttachment.objects.create(
                    email_campaign=campaign,
                    file=file,
                    original_filename=original_filename,
                    # Let the model handle content_type and file_size
                )
            except Exception as e:
                # Log the error but don't fail the entire request
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error processing file {getattr(file, 'name', 'unknown')}: {str(e)}")
                # Optionally, you could collect these errors and include them in the response
                
        return campaign
