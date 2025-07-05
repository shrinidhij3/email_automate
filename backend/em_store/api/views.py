import os
from rest_framework import status, viewsets, mixins, permissions
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import FileResponse

from campaigns.models import EmailCampaign, CampaignEmailAttachment
from .serializers import EmailCampaignSerializer, CampaignEmailAttachmentSerializer

# Constants for file uploads
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg',
    'image/png',
    'text/plain',
]

class EmailCampaignViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    API endpoint for managing email campaigns.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = EmailCampaignSerializer
    """
    API endpoint that allows email campaigns to be viewed or edited.
    Supports file uploads and handles provider-specific configurations.
    """
    queryset = EmailCampaign.objects.all()
    serializer_class = EmailCampaignSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """
        Check if an email exists in the campaigns_emailcampaign table.
        Returns a simple response indicating if the email exists.
        """
        email = self.request.query_params.get('email')
        if not email:
            return EmailCampaign.objects.none()
            
        # Simple check if email exists in the table
        exists = EmailCampaign.objects.filter(email__iexact=email).exists()
        return EmailCampaign.objects.filter(pk=-1) if not exists else EmailCampaign.objects.filter(email__iexact=email)

    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        if self.request.user.is_authenticated:
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()  # This will use the default (null for created_by)

    def _validate_file(self, file):
        """Validate file size and type."""
        if file.size > MAX_UPLOAD_SIZE:
            return False, 'File size exceeds the maximum allowed size (10MB)'
        
        if file.content_type not in ALLOWED_FILE_TYPES:
            return False, f'File type {file.content_type} is not allowed. Allowed types: {ALLOWED_FILE_TYPES}'
            
        return True, ''

    def create(self, request, *args, **kwargs):
        """Handle campaign creation with file uploads."""
        # Handle multipart form data
        if request.content_type.startswith('multipart/form-data'):
            # Handle file uploads
            files = request.FILES.getlist('files[]')
            
            # Validate files
            for file in files:
                is_valid, error = self._validate_file(file)
                if not is_valid:
                    return Response(
                        {'detail': error},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Convert QueryDict to mutable and add files to data
            data = request.data.copy()
            data.setlist('files', files)
            
            # Handle provider-specific configurations
            provider = data.get('provider')
            if provider and provider != 'custom':
                provider_config = PROVIDER_CONFIGS.get(provider, {})
                for field in ['smtp_host', 'smtp_port', 'use_ssl']:
                    if field in provider_config and not data.get(field):
                        data[field] = provider_config[field]
            
            # Ensure required fields are present
            if 'subject' not in data:
                data['subject'] = f"Campaign: {data.get('name', 'New Campaign')}"
            if 'body' not in data:
                data['body'] = data.get('notes', '')
            # Only set created_by if user is authenticated
            if not self.request.user.is_authenticated:
                data.pop('created_by', None)
            
            serializer = self.get_serializer(data=data)
        else:
            # Handle JSON data
            serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Include the full campaign data in the response
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        try:
            # Save the campaign with the authenticated user if available
            if self.request.user.is_authenticated:
                instance = serializer.save(created_by=self.request.user)
            else:
                instance = serializer.save()
            
            # Handle file uploads if any
            if 'files[]' in self.request.FILES:
                for file in self.request.FILES.getlist('files[]'):
                    # Validate the file first
                    is_valid, error_msg = self._validate_file(file)
                    if not is_valid:
                        print(f"Skipping invalid file {file.name}: {error_msg}")
                        continue  # Skip invalid files
                    
                    try:
                        # Save the file
                        attachment = CampaignEmailAttachment(
                            email_campaign=instance,
                            file=file,
                            original_filename=file.name,
                            content_type=file.content_type,
                            file_size=file.size,
                            uploaded_by=self.request.user if self.request.user.is_authenticated else None
                        )
                        attachment.save()
                    except Exception as e:
                        # Log the error but don't fail the entire request
                        print(f"Error saving file {file.name}: {str(e)}")
            
            return instance
            
        except Exception as e:
            print(f"Error in perform_create: {str(e)}")
            raise  # Re-raise to let DRF handle the error

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upload_attachment(self, request, pk=None):
        """
        Upload a file to be attached to an email campaign.
        """
        try:
            campaign = self.get_object()
            file = request.FILES.get('file')
            
            if not file:
                return Response(
                    {'error': 'No file provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Validate the file
            is_valid, error_msg = self._validate_file(file)
            if not is_valid:
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Save the file
            try:
                attachment = CampaignEmailAttachment(
                    email_campaign=campaign,
                    original_filename=file.name,
                    content_type=file.content_type,
                    file_size=file.size,
                    uploaded_by=request.user
                )
                attachment.save_file(file)
                attachment.save()
                
                # Return the attachment details
                serializer = CampaignEmailAttachmentSerializer(attachment)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response(
                    {'error': f'Error saving file: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        attachment = CampaignEmailAttachment(
            email_campaign=campaign,
            original_filename=file.name,
            content_type=file.content_type,
            file_size=file.size,
        )
        attachment.save_file(file)
        
        return Response(
            {'id': attachment.id, 'filename': attachment.original_filename},
            status=status.HTTP_201_CREATED
        )

class CampaignEmailAttachmentViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    API endpoint for managing email campaign attachments.
    Supports filtering by campaign, file type, and search by filename.
    Users can only access their own campaign attachments.
    """
    serializer_class = CampaignEmailAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['content_type', 'email_campaign']
    search_fields = ['original_filename', 'content_type']
    ordering_fields = ['created_at', 'file_size', 'original_filename']
    
    def get_queryset(self):
        """
        Return only attachments that belong to the current user's campaigns.
        Also supports filtering by campaign ID and file type.
        """
        queryset = CampaignEmailAttachment.objects.filter(
            email_campaign__created_by=self.request.user
        )
        
        # Filter by campaign if specified in query params
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            queryset = queryset.filter(email_campaign_id=campaign_id)
            
        # Filter by file type if specified
        file_type = self.request.query_params.get('file_type')
        if file_type:
            queryset = queryset.filter(content_type__icontains=file_type)
            
        # Apply search if specified
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(original_filename__icontains=search)
            
        return queryset.order_by('-created_at')
        
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def download(self, request, pk=None):
        """
        Download the attachment file.
        This endpoint is public but should be protected by other means (e.g., signed URLs)
        in a production environment.
        """
        try:
            # Bypass the get_queryset filter to allow access to any attachment
            # WARNING: This makes all attachments publicly accessible if the URL is known
            attachment = CampaignEmailAttachment.objects.filter(pk=pk).first()
            
            if not attachment:
                return Response(
                    {'error': 'Attachment not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Verify the file exists
            if not attachment.file:
                return Response(
                    {'error': 'File not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Open the file in binary mode
            try:
                file_handle = attachment.file.open('rb')
            except FileNotFoundError:
                return Response(
                    {'error': 'File not found on server'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Create the response with appropriate headers
            response = FileResponse(file_handle, content_type=attachment.content_type)
            response['Content-Disposition'] = f'attachment; filename="{attachment.original_filename}"'
            response['Content-Length'] = attachment.file.size
            
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error downloading file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id is not None:
            queryset = queryset.filter(email_campaign_id=campaign_id)
        return queryset
