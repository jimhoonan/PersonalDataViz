from celery import shared_task
from celery_progress.backend import ProgressRecorder
from .models import Uploader, FileUpload
import time

@shared_task(bind=True)
def test_celery_progress_bar(self, seconds):
    progress_recorder = ProgressRecorder(self)
    for i in range(seconds):
        time.sleep(1)
        progress_recorder.set_progress(i + 1, seconds)
    return 'done'

@shared_task(bind=True)
def shared_upload_from_FileUpload(self,file_upload_id):
    file_upload = FileUpload.objects.get(pk=file_upload_id)
    Uploader.upload_from_zip(file_upload.uploaded_file,file_upload.user)