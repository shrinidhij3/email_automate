from rest_framework import serializers
from campaigns.models import EmailCampaign, CampaignEmailAttachment

class CampaignEmailAttachmentSerializer(serializers.ModelSerializer):
    download_url = serializers.URLField(source='get_download_url', read_only=True)
    
    class Meta:
        model = CampaignEmailAttachment
        fields = ['id', 'original_filename', 'content_type', 'file_size', 'created_at', 'download_url']
        read_only_fields = ['id', 'created_at', 'download_url']

class EmailCampaignSerializer(serializers.ModelSerializer):
    attachments = CampaignEmailAttachmentSerializer(many=True, read_only=True)
    files = serializers.ListField(
        child=serializers.FileField(max_length=100, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = EmailCampaign
        fields = [
            'id', 'name', 'email', 'password', 'provider', 'imap_host', 'imap_port',
            'smtp_host', 'smtp_port', 'use_ssl', 'notes', 'created_at',
            'updated_at', 'attachments', 'files'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'use_ssl': {'default': True}
        }
    
    def create(self, validated_data):
        files = validated_data.pop('files', [])
        instance = super().create(validated_data)
        
        # Handle file uploads
        for file in files:
            CampaignEmailAttachment.objects.create(
                email_campaign=instance,
                file=file,
                original_filename=file.name,
                content_type=file.content_type,
                file_size=file.size
            )
        
        return instance
