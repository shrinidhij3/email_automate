from django.db import migrations, models


def update_passwords(apps, schema_editor):
    """
    Update existing passwords to be encrypted if they're not already.
    Since we're now handling encryption in the model's save() method,
    we don't need to do anything in the data migration.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('unread_emails', '0010_auto_20230627_1023'),
    ]

    operations = [
        # Ensure the password field has the correct attributes
        migrations.AlterField(
            model_name='unreademail',
            name='password',
            field=models.CharField(
                blank=True,
                help_text='Email account password (encrypted in database)',
                max_length=1024,
                null=True,
            ),
        ),
        # Add the data migration that doesn't actually modify data
        migrations.RunPython(update_passwords, migrations.RunPython.noop),
    ]
