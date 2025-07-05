from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('unread_emails', '0007_add_updated_at_to_attachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='unreademail',
            name='use_ssl',
            field=models.BooleanField(default=True, help_text='Whether to use SSL/TLS for the connection'),
        ),
    ]
