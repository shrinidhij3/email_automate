import os
import logging
import magic
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
# Password hashing removed - storing in plaintext
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

from rest_framework import status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.decorators import api_view
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from .models import UnreadEmail, UnreadEmailAttachment
from .serializers import (
    UnreadEmailSerializer, 
    UnreadEmailCreateSerializer,
    FileUploadSerializer
)

logger = logging.getLogger(__name__)

class TestAPIView(APIView):
    """
    Simple test API view to verify the API is working
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get(self, request, format=None):
        return Response({
            'status': 'success',
            'message': 'Test API endpoint is working!',
            'method': 'GET',
            'data': request.query_params,
        })
        
    def post(self, request, format=None):
        return Response({
            'status': 'success',
            'message': 'Test API endpoint is working!',
            'method': 'POST',
            'data': request.data
        })

@api_view(['GET'])
@permission_classes([AllowAny])
def download_attachment(request, attachment_id):
    """
    Download a file attachment by ID
    Public endpoint - no authentication required
    """
    try:
        attachment = get_object_or_404(UnreadEmailAttachment, id=attachment_id)
        
        # Log the download attempt
        logger.info(f"User {request.user} downloading attachment {attachment_id} - {attachment.original_filename}")
        
        # Check if file exists
        if not attachment.file:
            return Response(
                {'error': 'File not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create the response with file data
        response = HttpResponse(attachment.file.read(), content_type=attachment.content_type)
        response['Content-Disposition'] = f'attachment; filename="{attachment.original_filename}"'
        response['Content-Length'] = attachment.file_size
        return response
        
    except Exception as e:
        logger.error(f"Error downloading file {attachment_id}: {e}", exc_info=True)
        return Response(
            {'error': 'Error downloading file'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class AdminSubmissionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = UnreadEmail
    template_name = 'admin/unreademail/submission_list.html'
    context_object_name = 'submissions'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
        
    def get_queryset(self):
        return UnreadEmail.objects.prefetch_related('attachments').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Email Submissions Admin',
            'has_permission': self.request.user.is_staff,
            'site_header': 'Email Submissions Admin',
            'site_title': 'Email Submissions',
            'site_url': '/',
            'is_popup': False,
            'is_nav_sidebar_enabled': False,
            'available_apps': [],
        })
        return context
    
    def get_template_names(self):
        # First try the admin template, fall back to our custom template
        return [
            'admin/unreademail/submission_list.html',
            'admin_submissions.html',
        ]


class UnreadEmailViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing unread email submissions
    """
    queryset = UnreadEmail.objects.all()
    serializer_class = UnreadEmailSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    http_method_names = ['get', 'post', 'head']  # Disable put/patch/delete
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Allow unauthenticated POST requests for form submissions and file uploads.
        """
        if self.action in ['create', 'upload_attachment']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
        
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action
        """
        if self.action == 'create':
            return UnreadEmailCreateSerializer
        return UnreadEmailSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new unread email submission with file attachments
        """
        logger.info(f"Starting create method. Request data keys: {request.data.keys()}")
        logger.info(f"Files in request: {request.FILES}")
        
        # Create a mutable copy of the request data
        data = request.data.copy()
        
        # The password will be encrypted in the model's save() method
        serializer = self.get_serializer(data=data)
        try:
            logger.info("Validating serializer data")
            serializer.is_valid(raise_exception=True)
            logger.info("Serializer validation passed")
            
            with transaction.atomic():
                # Create the unread email record using the serializer
                logger.info("Creating UnreadEmail instance")
                instance = serializer.save()
                logger.info(f"Created UnreadEmail instance with ID: {instance.id}")
                
                # Handle file uploads if any
                if 'files' in request.FILES:
                    file_list = request.FILES.getlist('files')
                    logger.info(f"Processing {len(file_list)} file(s)")
                    try:
                        self._handle_file_uploads(instance, file_list)
                        logger.info("Successfully processed file uploads")
                    except ValidationError as e:
                        logger.error(f"File validation error: {e}")
                        raise ValidationError({'files': str(e)})
                    except Exception as e:
                        logger.exception("Unexpected error in file upload handling")
                        raise
                else:
                    logger.info("No files to process")
                
                # Return the created instance
                logger.info("Serializing response")
                response_serializer = self.serializer_class(instance)
                logger.info("Returning successful response")
                return Response(
                    response_serializer.data, 
                    status=status.HTTP_201_CREATED
                )
                
        except ValidationError as e:
            logger.error(f"Validation error in UnreadEmailViewSet.create: {e}", exc_info=True)
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception("Unexpected error in UnreadEmailViewSet.create")
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser])
    def upload_attachment(self, request, pk=None):
        """
        Handle file uploads for an existing unread email submission
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"UPLOAD ATTACHMENT REQUEST - pk={pk}")
        logger.info(f"{'='*80}")
        logger.info(f"Request data: {request.data}")
        logger.info(f"Request FILES: {request.FILES}")
        
        try:
            # Log request headers for debugging
            logger.info(f"Request headers: {dict(request.headers)}")
            
            # Get the unread email instance
            try:
                instance = self.get_object()
                logger.info(f"Found unread email instance: {instance.id}")
            except UnreadEmail.DoesNotExist as e:
                logger.error(f"UnreadEmail {pk} not found")
                return Response(
                    {'error': f'Unread email submission not found: {str(e)}'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Log the incoming data for debugging
            logger.info(f"Request data keys: {list(request.data.keys())}")
            logger.info(f"Request FILES keys: {list(request.FILES.keys())}")
            
            # Get the uploaded file
            if 'file' not in request.FILES:
                error_msg = f"No file found in request.FILES. Available keys: {list(request.FILES.keys())}"
                logger.error(error_msg)
                return Response(
                    {'error': 'No file provided in the request', 'details': error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            uploaded_file = request.FILES['file']
            logger.info(f"Processing file: {uploaded_file.name} (size: {uploaded_file.size} bytes, type: {uploaded_file.content_type})")
            
            try:
                # Validate the file
                self._validate_file(uploaded_file)
                logger.info("File validation passed")
                
                # Create and save the attachment with file data
                attachment = UnreadEmailAttachment(
                    unread_email=instance,
                    original_filename=uploaded_file.name,
                    content_type=uploaded_file.content_type or 'application/octet-stream',
                    file_size=uploaded_file.size
                )
                
                # Save file data to the database
                logger.info("Saving file to database...")
                attachment.save_file(uploaded_file)
                logger.info(f"File saved successfully with ID: {attachment.id}")
                
                return Response(
                    {
                        'id': str(attachment.id),
                        'filename': attachment.original_filename,
                        'size': attachment.file_size,
                        'content_type': attachment.content_type,
                        'created_at': attachment.created_at.isoformat(),
                        'message': 'File uploaded successfully'
                    },
                    status=status.HTTP_201_CREATED
                )
                
            except ValidationError as e:
                error_msg = f"File validation failed: {str(e)}"
                logger.error(error_msg)
                logger.error(f"Validation errors: {getattr(e, 'message_dict', str(e))}")
                return Response(
                    {
                        'error': 'File validation failed',
                        'details': str(e),
                        'validation_errors': getattr(e, 'message_dict', None)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except Exception as e:
            error_msg = f"Unexpected error in upload_attachment: {str(e)}"
            logger.exception(error_msg)
            return Response(
                {
                    'error': 'An error occurred while processing your file',
                    'details': str(e),
                    'type': type(e).__name__
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            logger.info(f"{'='*80}\n")
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def download_attachment(self, request, pk=None, attachment_id=None):
        """
        Download a file attachment by ID
        Public endpoint - no authentication required
        """
        try:
            # Get the unread email instance (not strictly needed but good for validation)
            unread_email = self.get_object()
            
            # Get the attachment
            try:
                attachment = unread_email.attachments.get(id=attachment_id)
            except UnreadEmailAttachment.DoesNotExist:
                return Response(
                    {'error': 'Attachment not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Log the download attempt
            logger.info(f"User {request.user} downloading attachment {attachment_id} - {attachment.original_filename}")
            
            # Check if file exists
            if not attachment.file:
                return Response(
                    {'error': 'File not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create the response with file data
            response = HttpResponse(attachment.file.read(), content_type=attachment.content_type)
            response['Content-Disposition'] = f'attachment; filename="{attachment.original_filename}"'
            response['Content-Length'] = attachment.file_size
            return response
            
        except Exception as e:
            logger.error(f"Error downloading file {attachment_id}: {e}", exc_info=True)
            return Response(
                {'error': 'Error downloading file'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _validate_file(self, uploaded_file):
        """Validate file size and type"""
        # Check file size
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)
        if uploaded_file.size > max_size:
            raise ValidationError(f'File size exceeds maximum allowed size of {max_size} bytes')
        
        # Get the declared content type from the upload
        declared_type = (uploaded_file.content_type or '').lower()
        
        # Get allowed types from settings (convert to lowercase for case-insensitive comparison)
        allowed_types = [t.lower() for t in getattr(settings, 'ALLOWED_FILE_TYPES', [])]
        
        # If declared type is allowed, accept it
        if declared_type in allowed_types:
            logger.debug(f"File type {declared_type} is in allowed types")
            return
            
        # Read file content for MIME type detection
        file_content = uploaded_file.read(1024)
        detected_type = magic.from_buffer(file_content, mime=True).lower()
        uploaded_file.seek(0)  # Reset file pointer
        
        logger.debug(f"File validation - Declared: {declared_type}, Detected: {detected_type}")
        
        # Special handling for PDF files
        if detected_type == 'application/pdf' or declared_type == 'application/pdf':
            if 'application/pdf' in allowed_types:
                logger.debug("PDF file accepted")
                return
        
        # Special handling for Office Open XML files (.docx, .xlsx, etc.)
        is_office_xml = (
            detected_type == 'application/zip' and 
            any(t in (declared_type or '') for t in [
                'vnd.openxmlformats-officedocument',
                'application/msword',
                'application/vnd.ms-excel',
                'application/vnd.ms-powerpoint',
                'application/vnd.openxmlformats',
                'officedocument',
                'wordprocessingml',
                'spreadsheetml',
                'presentationml',
                'opendocument',
                'ms-office',
                'office',
                'msword',
                'excel',
                'powerpoint'
            ])
        )
        
        # If detected type is allowed or it's an Office XML file, accept it
        if detected_type in allowed_types or is_office_xml:
            logger.debug(f"File accepted - Detected: {detected_type}, Office XML: {is_office_xml}")
            return
        
        # Additional check for text files
        if detected_type.startswith('text/') and 'text/plain' in allowed_types:
            logger.debug("Text file accepted")
            return
            
        # If we get here, the file type is not allowed
        error_msg = (
            f'File type not allowed. Detected: {detected_type}, Declared: {declared_type}. ' \
            f'Allowed types: {allowed_types}'
        )
        logger.warning(error_msg)
        raise ValidationError(error_msg)
    
    def _handle_file_uploads(self, unread_email: UnreadEmail, files: List) -> None:
        """
        Handle multiple file uploads with validation and store in Cloudflare R2
        """
        logger.info(f"Starting _handle_file_uploads for {len(files)} files")
        
        for i, uploaded_file in enumerate(files, 1):
            file_info = f"File {i}/{len(files)}: {uploaded_file.name} ({uploaded_file.size} bytes, {uploaded_file.content_type})"
            logger.info(f"Processing {file_info}")
            
            try:
                # Validate file
                logger.debug(f"Validating {uploaded_file.name}")
                self._validate_file(uploaded_file)
                logger.debug(f"Validation passed for {uploaded_file.name}")
                
                # Create the attachment with the file
                logger.debug(f"Creating UnreadEmailAttachment for {uploaded_file.name}")
                attachment = UnreadEmailAttachment(
                    unread_email=unread_email,
                    file=uploaded_file,
                    original_filename=uploaded_file.name,
                    content_type=uploaded_file.content_type or 'application/octet-stream',
                    file_size=uploaded_file.size
                )
                
                # Save the attachment (this will trigger the save method which generates the Cloudflare URL)
                logger.debug(f"Saving file {uploaded_file.name} to storage")
                attachment.save()
                
                logger.info(f"Successfully saved file {uploaded_file.name} with ID {attachment.id}")
                logger.debug(f"Cloudflare URL: {attachment.download_url}")
                
            except ValidationError as e:
                logger.warning(f"Skipping invalid file {uploaded_file.name}: {str(e)}")
                logger.debug(f"Validation error details:", exc_info=True)
                continue
                
            except Exception as e:
                logger.error(f"Error processing file {uploaded_file.name}: {str(e)}", exc_info=True)
                continue
                
        logger.info(f"Completed processing {len(files)} files")
    
    def _save_uploaded_file(self, unread_email: UnreadEmail, uploaded_file) -> str:
        """
        This method is no longer needed as we're storing files in the database
        Keeping it for backward compatibility but it won't be called
        """
        raise NotImplementedError("File storage now handled in the database")
        return str(file_path.relative_to(settings.MEDIA_ROOT))
        
    @action(detail=False, methods=['post'])
    def bulk_create(self, request, *args, **kwargs):
        """
        Handle bulk creation of unread email entries
        """
        if not isinstance(request.data, list):
            return Response(
                {'error': 'Expected a list of items'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        created = []
        errors = []
        
        for index, item in enumerate(request.data):
            try:
                # Validate required fields
                if not all(key in item for key in ['name', 'email']):
                    errors.append({
                        'index': index,
                        'error': 'Missing required fields (name and email)',
                        'item': item
                    })
                    continue
                    
                # Create the unread email record
                unread_email = UnreadEmail.objects.create(
                    name=item['name'].strip(),
                    email=item['email'].strip().lower(),
                    password='default_password'  # Store plaintext password
                )
                
                created.append(UnreadEmailSerializer(unread_email).data)
                
            except Exception as e:
                errors.append({
                    'index': index,
                    'error': str(e),
                    'item': item
                })
        
        if errors and not created:
            return Response(
                {'errors': errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response({
            'created': len(created),
            'errors': len(errors),
            'results': created,
            'error_details': errors if errors else None
        }, status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED)