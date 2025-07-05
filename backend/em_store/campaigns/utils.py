from django.db import connection
import logging

logger = logging.getLogger(__name__)

def ensure_sequence_sync():
    """
    Ensures the sequence for campaign email attachments is in sync with the max ID.
    Should be called after bulk operations that might create records.
    """
    try:
        with connection.cursor() as cursor:
            # Get current max ID
            cursor.execute("SELECT MAX(id) FROM campaigns_campaignemailattachment;")
            max_id = cursor.fetchone()[0] or 0
            
            # Get current sequence value
            cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
            current_sequence = cursor.fetchone()[0]
            
            if max_id >= current_sequence:
                new_sequence = max_id + 1
                logger.info(f"Updating sequence from {current_sequence} to {new_sequence}")
                
                # Set the sequence to max_id + 1
                cursor.execute(
                    "SELECT setval('campaigns_campaignemailattachment_id_seq', %s, false);",
                    [new_sequence]
                )
                return True
            return False
                
    except Exception as e:
        logger.error(f"Error syncing sequence: {e}", exc_info=True)
        return False
