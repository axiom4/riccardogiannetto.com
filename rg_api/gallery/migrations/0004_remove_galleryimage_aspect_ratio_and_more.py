# Generated by Django 5.0.4 on 2024-05-03 07:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0003_alter_gallery_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='galleryimage',
            name='aspect_ratio',
        ),
        migrations.RemoveField(
            model_name='galleryimage',
            name='short_name',
        ),
    ]
