from celery import shared_task
from .models import Uploader, FileUpload
import time


@shared_task(bind=True)
def shared_upload_from_FileUpload(self,file_upload_id):
    file_upload = FileUpload.objects.get(pk=file_upload_id)
    Uploader.upload_from_zip(file_upload.uploaded_file,file_upload.user)