from rest_framework import serializers
from .models import UnreadEmail, UnreadEmailAttachment

class UnreadEmailAttachmentSerializer(serializers.ModelSerializer):
    download_url = serializers.URLField(read_only=True)
    file_url = serializers.FileField(source='file', read_only=True)
    
    class Meta:
        model = UnreadEmailAttachment
        fields = [
            'id', 'original_filename', 'file_size', 'content_type', 
            'created_at', 'download_url', 'file_url'
        ]
        read_only_fields = [
            'id', 'file_size', 'content_type', 'created_at', 
            'download_url', 'file_url'
        ]

class UnreadEmailSerializer(serializers.ModelSerializer):
    attachments = UnreadEmailAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = UnreadEmail
        fields = [
            'id', 'name', 'email', 'is_processed', 'notes',
            'created_at', 'updated_at', 'attachments',
            'provider', 'imap_host', 'imap_port', 'smtp_host', 'smtp_port',
            'secure', 'use_ssl'
        ]
        read_only_fields = [
            'id', 'is_processed', 'created_at', 'updated_at', 'attachments'
        ]

class UnreadEmailCreateSerializer(serializers.ModelSerializer):
    # Password field that will be encrypted before saving
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = UnreadEmail
        fields = [
            'name', 'email', 'password', 'provider', 'imap_host', 'imap_port',
            'smtp_host', 'smtp_port', 'secure', 'use_ssl', 'notes'
        ]
        extra_kwargs = {
            'secure': {'required': False, 'default': True},
            'use_ssl': {'required': False, 'default': True},
            'imap_host': {'required': False},
            'imap_port': {'required': False},
            'smtp_host': {'required': False},
            'smtp_port': {'required': False},
            'notes': {'required': False}
        }
    
    def create(self, validated_data):
        # The password will be encrypted in the model's save() method
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # The password will be encrypted in the model's save() method
        return super().update(instance, validated_data)

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    original_filename = serializers.CharField(max_length=255)
    content_type = serializers.CharField(max_length=100)
