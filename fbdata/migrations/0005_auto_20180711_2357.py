# Generated by Django 2.0.6 on 2018-07-12 04:57

from django.db import migrations, models
import fbdata.models


class Migration(migrations.Migration):

    dependencies = [
        ('fbdata', '0004_fileupload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='uploaded_file',
            field=models.FileField(max_length=500, upload_to=fbdata.models.user_directory_path),
        ),
    ]
