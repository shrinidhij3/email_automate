import logging
import traceback
from django.db import connection
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from campaigns.models import EmailCampaign
from .models import EmailEntry
from .serializers import EmailEntrySerializer

# Set up logging
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

def log_database_info():
    """Log database connection and table information"""
    try:
        logger.debug("Getting database connection info...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user, version()")
            db_info = cursor.fetchone()
            logger.info(f"Database Info: {db_info}")
            
            logger.debug("Fetching table list...")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"Available tables: {tables}")
            
            if 'email_auto' in tables:
                logger.debug("Checking email_auto table...")
                cursor.execute("SELECT COUNT(*) FROM email_auto")
                count = cursor.fetchone()[0]
                logger.info(f"email_auto table has {count} rows")
                
                # Get column information
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'email_auto'
                """)
                columns = {row[0]: row[1] for row in cursor.fetchall()}
                logger.info(f"email_auto columns: {columns}")
    except Exception as e:
        error_msg = f"Error checking database info: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return error_msg
    return "Database check completed"

class EmailEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows email entries to be viewed or edited.
    """
    queryset = EmailEntry.objects.all()
    serializer_class = EmailEntrySerializer
    permission_classes = [AllowAny]  # For development only
    
    def get_serializer_context(self):
        """Add request and campaign_id to the serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        
        # Get campaign_id from query params
        campaign_id = self.request.query_params.get('campaign_id')
        
        # Only try to get campaign_id from request data if it's a single entry (dict)
        if not campaign_id and hasattr(self.request, 'data') and isinstance(self.request.data, dict):
            campaign_id = self.request.data.get('campaign_id')
        
        # If we're in a bulk upload (list), the campaign_id should be in the query params
        # or in each individual entry, which will be handled in the create method
        if campaign_id:
            try:
                campaign = EmailCampaign.objects.get(id=campaign_id)
                context['campaign'] = campaign
            except (EmailCampaign.DoesNotExist, ValueError) as e:
                logger.warning(f"Campaign with ID {campaign_id} not found: {str(e)}")
        return context
        
    def create(self, request, *args, **kwargs):
        logger.info("\n" + "="*80)
        logger.info("START: EmailEntryViewSet.create")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Content type: {request.content_type}")
        logger.info(f"Query params: {dict(request.query_params)}")
        logger.info(f"Request data: {request.data}")
        
        # Check for campaign_id in query params or request data
        campaign_id = None
        campaign = None
        
        # First try to get campaign_id from query params
        campaign_id = request.query_params.get('campaign_id')
        
        # If not in query params, try to get from request data (for single entry)
        if not campaign_id and isinstance(request.data, dict):
            campaign_id = request.data.get('campaign_id')
        
        # If we have a campaign_id, try to get the campaign
        if campaign_id:
            try:
                campaign = EmailCampaign.objects.get(id=campaign_id)
                logger.info(f"Processing request for campaign: {campaign.name} (ID: {campaign.id})")
            except (EmailCampaign.DoesNotExist, ValueError) as e:
                logger.warning(f"Campaign with ID {campaign_id} not found - {str(e)}")
            except Exception as e:
                logger.error(f"Error fetching campaign: {str(e)}")
        else:
            logger.info("No campaign_id provided in request")
        
        try:
            # Log database info
            logger.info("\n[1/5] Checking database connection...")
            db_status = log_database_info()
            logger.info(f"Database status: {db_status}")
            
            # Log incoming request data
            logger.info("\n[2/5] Processing request data...")
            logger.info(f"Request data type: {type(request.data)}")
            logger.info(f"Request data: {request.data}")
            
            # Validate input data
            if not isinstance(request.data, (dict, list)):
                error_msg = "Invalid data format. Expected object or array of objects."
                logger.error(f"Validation error: {error_msg}")
                return Response(
                    {"error": error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Handle single entry
            if isinstance(request.data, dict):
                logger.info("\n[3/5] Processing single entry...")
                data = request.data.copy()
                if campaign:
                    data['campaign'] = campaign.id
                return self._handle_single_entry(data)
            
            # Handle bulk entries (list of entries)
            elif isinstance(request.data, list):
                logger.info(f"\n[3/5] Processing {len(request.data)} bulk entries...")
                entries = request.data
                
                # Validate all entries are dictionaries
                if not all(isinstance(entry, dict) for entry in entries):
                    error_msg = "Invalid bulk data format. Expected array of objects."
                    logger.error(f"Validation error: {error_msg}")
                    return Response(
                        {"error": error_msg},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Add campaign to each entry if available
                if campaign:
                    for entry in entries:
                        entry['campaign'] = campaign.id
                        
                return self._handle_bulk_entries(entries)
            
            # Invalid data format
            error_msg = "Invalid data format. Expected object or array of objects."
            logger.error(f"Validation error: {error_msg}")
            return Response(
                {"error": error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            error_msg = f"Error in EmailEntryViewSet.create: {str(e)}"
            logger.error(f"\n[ERROR] {error_msg}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            
            # Log more details about the exception
            if hasattr(e, '__dict__'):
                logger.error(f"Exception details: {e.__dict__}")
                
            return Response(
                {
                    "error": "Internal server error",
                    "details": str(e),
                    "type": type(e).__name__
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            logger.info("\n[5/5] Request processing completed")
            logger.info("="*80 + "\n")
    
    def _check_duplicate_email(self, email):
        """Check if email already exists in the database"""
        return EmailEntry.objects.filter(email__iexact=email).exists()

    def _handle_single_entry(self, data):
        """Handle creation of a single email entry"""
        try:
            logger.info("\n[4/5] Validating single entry...")
            
            # Check for duplicate email
            email = data.get('email', '').strip().lower()
            if self._check_duplicate_email(email):
                return Response(
                    {
                        "error": "Email already exists",
                        "email": email,
                        "status": "duplicate"
                    },
                    status=status.HTTP_409_CONFLICT
                )
            
            serializer = self.get_serializer(data=data)
            logger.debug("Running serializer validation...")
            serializer.is_valid(raise_exception=True)
            
            logger.debug("Creating database record...")
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            logger.info("Single entry created successfully")
            logger.debug(f"Created entry: {serializer.data}")
            
            return Response(
                {
                    "message": "Email added successfully",
                    "email": email,
                    "status": "created"
                },
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except Exception as e:
            logger.error(f"Error in _handle_single_entry: {str(e)}")
            logger.error(f"Validation errors: {getattr(serializer, 'errors', 'No validation errors')}")
            raise
    
    def _handle_bulk_entries(self, data):
        """Handle bulk creation of email entries with duplicate checking"""
        logger.info(f"Processing {len(data)} bulk entries")
        
        # Convert all emails to lowercase for case-insensitive comparison and validate client_email
        for entry in data:
            if 'email' in entry:
                entry['email'] = entry['email'].strip().lower()
            
            # Validate client_email format if present
            client_email = entry.get('client_email')
            if client_email and not isinstance(client_email, str):
                return Response(
                    {
                        "error": f"Invalid client_email format for entry: {entry.get('email')}",
                        "status": "invalid_client_email"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check for duplicate emails in the request itself
        seen_emails = set()
        duplicate_in_request = []
        for entry in data:
            email = entry.get('email')
            if not email:
                continue
                
            if email in seen_emails:
                duplicate_in_request.append(email)
            seen_emails.add(email)
        
        if duplicate_in_request:
            return Response(
                {
                    "error": "Duplicate emails in the uploaded file",
                    "duplicate_emails": duplicate_in_request,
                    "status": "duplicate_in_request"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for existing emails in the database
        existing_emails = set(
            EmailEntry.objects.filter(
                email__in=seen_emails
            ).values_list('email', flat=True)
        )
        
        # Separate new and duplicate entries
        new_entries = []
        duplicate_entries = []
        
        for entry in data:
            if entry['email'] in existing_emails:
                duplicate_entries.append(entry['email'])
            else:
                new_entries.append(entry)
        
        # Only process new entries
        created_count = 0
        serializer = None
        
        if new_entries:
            try:
                logger.info(f"Processing {len(new_entries)} new entries")
                # Initialize serializer with the new entries
                serializer = self.get_serializer(data=new_entries, many=True)
                serializer.is_valid(raise_exception=True)
                
                # Log the data being saved
                logger.debug(f"Saving {len(new_entries)} valid entries")
                self.perform_create(serializer)
                created_count = len(serializer.data)
                logger.info(f"Successfully created {created_count} entries")
                
            except Exception as e:
                error_msg = f"Error creating entries: {str(e)}"
                logger.error(error_msg)
                
                # Get validation errors if serializer was initialized
                validation_errors = {}
                if serializer is not None and hasattr(serializer, 'errors'):
                    validation_errors = serializer.errors
                    logger.error(f"Validation errors: {validation_errors}")
                
                logger.error(f"Exception type: {type(e).__name__}")
                logger.error(f"Traceback:\n{traceback.format_exc()}")
                
                # If we have a validation error, include details in the response
                if hasattr(e, 'detail') and isinstance(e.detail, dict):
                    return Response(
                        {
                            "error": "Validation error",
                            "details": e.detail,
                            "created": created_count,
                            "status": "validation_error"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # For serializer validation errors
                if validation_errors:
                    return Response(
                        {
                            "error": "Validation error",
                            "details": validation_errors,
                            "created": created_count,
                            "status": "validation_error"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # For other errors, return a generic error message
                return Response(
                    {
                        "error": "Failed to create some entries",
                        "details": str(e),
                        "created": created_count,
                        "status": "error"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Prepare response
        response_data = {
            "created": created_count,
            "duplicates": len(duplicate_entries),
            "duplicate_emails": duplicate_entries,
            "total_processed": len(data),
            "status": "completed"
        }
        
        if duplicate_entries:
            response_data["message"] = (
                f"Successfully created {created_count} entries. "
                f"Skipped {len(duplicate_entries)} duplicate(s)."
            )
            status_code = status.HTTP_207_MULTI_STATUS
        else:
            response_data["message"] = f"Successfully created {created_count} entries."
            status_code = status.HTTP_201_CREATED
        
        logger.info(f"Bulk upload completed: {response_data}")
        
        return Response(
            response_data,
            status=status_code,
            headers={"X-Duplicates": ",".join(duplicate_entries) if duplicate_entries else ""}
        )

