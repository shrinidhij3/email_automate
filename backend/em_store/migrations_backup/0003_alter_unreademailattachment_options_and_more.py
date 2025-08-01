# Generated by Django 4.2.7 on 2025-06-20 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unread_emails', '0002_store_files_in_database'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='unreademailattachment',
            options={'ordering': ['-created_at'], 'verbose_name': 'Attachment', 'verbose_name_plural': 'Attachments'},
        ),
        migrations.AddField(
            model_name='unreademailattachment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='unreademailattachment',
            name='file_size',
            field=models.PositiveIntegerField(help_text='Size of the file in bytes'),
        ),
        migrations.AlterModelTable(
            name='unreademail',
            table='unread_emails_unreademail',
        ),
        migrations.AlterModelTable(
            name='unreademailattachment',
            table='unread_emails_unreademailattachment',
        ),
    ]
