# Generated by Django 4.2.7 on 2025-06-20 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_entry', '0002_remove_emailentry_is_active_remove_emailentry_source_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='emailentry',
            options={'ordering': ['date_of_signup', 'id'], 'verbose_name': 'Email Entry', 'verbose_name_plural': 'Email Entries'},
        ),
        migrations.AlterField(
            model_name='emailentry',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
