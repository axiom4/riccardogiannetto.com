# Generated by Django 5.0.5 on 2024-05-07 06:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0012_alter_imagegallery_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imagegallery',
            old_name='exposure_time',
            new_name='shutter_speed',
        ),
    ]