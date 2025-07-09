import logging
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.exceptions import ValidationError

from campaigns.models import CampaignEmailAttachment, EmailCampaign
from .serializers import CampaignEmailAttachmentSerializer

logger = logging.getLogger(__name__)

class CampaignEmailAttachmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing email campaign attachments.
    """
    queryset = CampaignEmailAttachment.objects.all()
    serializer_class = CampaignEmailAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        """Filter attachments by campaign and user permissions."""
        queryset = super().get_queryset()
        campaign_id = self.request.query_params.get('campaign_id')
        
        if campaign_id:
            queryset = queryset.filter(email_campaign_id=campaign_id)
            
        # Only show attachments for campaigns the user has access to
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                email_campaign__created_by=self.request.user
            )
            
        return queryset

    def perform_create(self, serializer):
        """Handle file upload to R2 and associate with campaign."""
        campaign_id = self.request.data.get('email_campaign')
        if not campaign_id:
            raise ValidationError("email_campaign is required")
            
        # Verify the campaign exists and user has permission
        campaign = get_object_or_404(
            EmailCampaign.objects.filter(created_by=self.request.user),
            pk=campaign_id
        )
        
        # Save the attachment
        serializer.save(email_campaign=campaign)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download the attachment file from R2."""
        attachment = self.get_object()
        
        # Check permissions
        if not request.user.is_superuser and attachment.email_campaign.created_by != request.user:
            return Response(
                {"detail": "You do not have permission to access this file."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get the file from R2
        try:
            file = attachment.file
            response = FileResponse(file)
            
            # Set content type and disposition
            response['Content-Type'] = attachment.content_type or 'application/octet-stream'
            response['Content-Disposition'] = f'attachment; filename="{attachment.original_filename}"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error serving file {attachment.file.name}: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Error retrieving file."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def upload(self, request, pk=None):
        """Handle file upload for an existing campaign."""
        campaign = get_object_or_404(
            EmailCampaign.objects.filter(created_by=request.user),
            pk=pk
        )
        
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                {"detail": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create the attachment
            attachment = CampaignEmailAttachment(
                email_campaign=campaign,
                file=file_obj,
                original_filename=file_obj.name,
                content_type=file_obj.content_type
            )
            attachment.save()
            
            return Response(
                CampaignEmailAttachmentSerializer(attachment).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}", exc_info=True)
            return Response(
                {"detail": f"Error uploading file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
