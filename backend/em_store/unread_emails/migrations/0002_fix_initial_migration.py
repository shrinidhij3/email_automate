from django.db import migrations, models


def mark_tables_exist(apps, schema_editor):
    """Mark that the tables already exist in the database."""
    # This function will be run when applying the migration
    pass


def reverse_mark_tables_exist(apps, schema_editor):
    """No-op for reversing the migration."""
    pass


class Migration(migrations.Migration):
    """Migration to mark existing tables as already created."""

    dependencies = [
        ('unread_emails', '0001_initial'),
    ]

    operations = [
        # This will mark all tables in the migration as already existing
        migrations.RunPython(
            mark_tables_exist,
            reverse_mark_tables_exist,
        ),
    ]
