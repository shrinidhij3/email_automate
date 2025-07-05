from django.db import migrations, models
import django.db.models.deletion
import unread_emails.models


def migrate_files_to_binary(apps, schema_editor):
    """
    Migrate files from filesystem to binary data in the database
    """
    UnreadEmailAttachment = apps.get_model('unread_emails', 'UnreadEmailAttachment')
    
    # Only process attachments that have a file path but no binary data
    for attachment in UnreadEmailAttachment.objects.filter(file_data__isnull=True):
        try:
            if attachment.file:
                with attachment.file.open('rb') as f:
                    attachment.file_data = f.read()
                attachment.save()
        except Exception as e:
            print(f"Error migrating file {attachment.file.name}: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('unread_emails', '0001_initial'),
    ]

    operations = [
        # Add the new file_data field (temporarily nullable)
        migrations.AddField(
            model_name='unreademailattachment',
            name='file_data',
            field=models.BinaryField(blank=True, null=True, help_text='Binary file data'),
        ),
        
        # Run the data migration
        migrations.RunPython(migrate_files_to_binary, migrations.RunPython.noop),
        
        # Remove the old file field
        migrations.RemoveField(
            model_name='unreademailattachment',
            name='file',
        ),
        
        # Make file_data non-nullable
        migrations.AlterField(
            model_name='unreademailattachment',
            name='file_data',
            field=models.BinaryField(help_text='Binary file data'),
        ),
    ]
