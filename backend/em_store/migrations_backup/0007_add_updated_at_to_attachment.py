from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('unread_emails', '0006_add_secure_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='unreademailattachment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
