# Generated by Django 4.2.7 on 2025-07-03 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0002_alter_emailcampaign_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaignemailattachment',
            name='download_url',
            field=models.URLField(blank=True, help_text='Direct download URL for the file', max_length=500, null=True),
        ),
    ]
