# myapp/storages_backends.py
from storages.backends.s3boto3 import S3Boto3Storage

class S3VideoStorage(S3Boto3Storage):
    location = ''
    file_overwrite = False
