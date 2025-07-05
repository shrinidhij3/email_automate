import logging
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import connection

from .models import EmailCampaign, CampaignEmailAttachment
from .serializers import EmailCampaignSerializer, CampaignEmailAttachmentSerializer


def check_and_fix_sequence():
    """
    Check if the sequence needs to be updated and fix it if necessary.
    Returns True if the sequence was fixed, False otherwise.
    """
    with connection.cursor() as cursor:
        # Get current max ID
        cursor.execute("SELECT COALESCE(MAX(id), 0) FROM campaigns_campaignemailattachment")
        max_id = cursor.fetchone()[0]
        
        # Get current sequence value
        cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq")
        current_seq = cursor.fetchone()[0]
        
        logger.info(f"Current max ID: {max_id}, Current sequence: {current_seq}")
        
        # If sequence needs updating
        if current_seq <= max_id:
            new_seq = max_id + 1
            logger.warning(f"Sequence needs update. Setting sequence to {new_seq}")
            cursor.execute(
                "ALTER SEQUENCE campaigns_campaignemailattachment_id_seq RESTART WITH %s",
                [new_seq]
            )
            logger.info(f"Sequence updated to {new_seq}")
            return True
    return False

logger = logging.getLogger(__name__)

class EmailCampaignViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing email campaigns.
    """
    queryset = EmailCampaign.objects.all()
    serializer_class = EmailCampaignSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only campaigns created by the current user."""
        return self.queryset.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a new email campaign with optional file attachments.
        """
        logger.info("=== New Campaign Creation Request ===")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Content type: {request.content_type}")
        logger.info(f"User: {request.user} (Authenticated: {request.user.is_authenticated})")
        
        # Log request data (safely)
        log_data = request.data.copy()
        if 'password' in log_data:
            log_data['password'] = '***REDACTED***'
        logger.info(f"Request data: {log_data}")
        
        # Log files info
        files = request.FILES.getlist('files', [])
        logger.info(f"Found {len(files)} files in request")
        for i, file in enumerate(files, 1):
            logger.info(f"  File {i}: {file.name} ({file.size} bytes, {file.content_type})")
        
        try:
            # Prepare data for serializer
            data = request.data.copy()
            logger.info(f"Prepared data for serializer: {data}")
            
            # Create and validate the campaign
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                logger.error(f"Validation errors: {serializer.errors}")
                return Response(
                    {"error": "Validation failed", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save the campaign
            self.perform_create(serializer)
            campaign = serializer.instance
            logger.info(f"Campaign created with ID: {campaign.id}")
            
            # Process file uploads if any
            if files:
                logger.info(f"Processing {len(files)} file(s) for campaign {campaign.id}")
                successful_uploads = 0
                
                for file in files:
                    try:
                        # Validate file type and size
                        if file.size > 10 * 1024 * 1024:  # 10MB limit
                            logger.warning(f"File {file.name} exceeds size limit (10MB)")
                            continue
                            
                        # Create attachment with unique filename to avoid conflicts
                        try:
                            attachment = CampaignEmailAttachment.objects.create(
                                email_campaign=campaign,
                                file=file,
                                original_filename=file.name,
                                file_size=file.size,
                                content_type=file.content_type or 'application/octet-stream'
                            )
                            successful_uploads += 1
                            logger.info(f"Created attachment ID {attachment.id} for file: {file.name}")
                        except Exception as e:
                            logger.error(f"Failed to create attachment for {file.name}: {str(e)}")
                            continue
                        
                    except Exception as e:
                        logger.error(f"Error processing file {file.name}: {str(e)}", exc_info=True)
                        continue
                
                logger.info(f"Successfully uploaded {successful_uploads}/{len(files)} files")
            
            # Get the updated campaign with attachments
            serializer = self.get_serializer(campaign)
            response_data = serializer.data
            logger.info("=== Campaign Creation Successful ===")
            
            return Response(
                response_data,
                status=status.HTTP_201_CREATED,
                headers=self.get_success_headers(serializer.data)
            )
            
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to create campaign", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def upload_attachments(self, request, pk=None):
        """Upload additional attachments to an existing campaign."""
        campaign = self.get_object()
        files = request.FILES.getlist('files')
        
        if not files:
            return Response(
                {"error": "No files provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check and fix sequence before creating attachments
        try:
            sequence_was_fixed = check_and_fix_sequence()
            if sequence_was_fixed:
                logger.info("Sequence was fixed before uploading new attachments")
        except Exception as e:
            logger.error(f"Error checking/fixing sequence: {str(e)}")
            # Continue with upload even if sequence check fails
        
        attachments = []
        for file in files:
            try:
                # Check file size before processing
                if file.size > 10 * 1024 * 1024:  # 10MB limit
                    logger.warning(f"File {file.name} exceeds size limit (10MB)")
                    continue
                    
                # Create attachment with error handling
                attachment = CampaignEmailAttachment.objects.create(
                    email_campaign=campaign,
                    file=file,
                    original_filename=file.name,
                    content_type=file.content_type or 'application/octet-stream',
                    file_size=file.size
                )
                attachments.append(attachment)
                logger.info(f"Successfully created attachment ID {attachment.id} for file: {file.name}")
                
            except Exception as e:
                logger.error(f"Failed to create attachment for {file.name}: {str(e)}", exc_info=True)
                # Continue with next file even if one fails
                continue
        
        if not attachments:
            return Response(
                {"error": "Failed to process any files"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CampaignEmailAttachmentSerializer(attachments, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def send_test(self, request, pk=None):
        """Send a test email for this campaign."""
        campaign = self.get_object()
        # TODO: Implement test email sending
        return Response(
            {"message": "Test email functionality coming soon"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def send_campaign(self, request, pk=None):
        """Send the campaign to all recipients."""
        campaign = self.get_object()
        # TODO: Implement campaign sending
        return Response(
            {"message": "Campaign sending functionality coming soon"},
            status=status.HTTP_200_OK
        )
