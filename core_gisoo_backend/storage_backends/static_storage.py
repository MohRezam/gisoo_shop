from storages.backends.s3boto3 import S3Boto3Storage

# this is for if you want to save static files like admin panel statics in s3 which is not most of the time needed!
class StaticStorage(S3Boto3Storage):
    BASE_LOCATION = "static"
    location = "static"
