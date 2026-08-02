from decouple import config

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = config("AWS_BUCKET_NAME", "")
AWS_S3_HOST = config("AWS_URL", "")
AWS_S3_ENDPOINT_URL = config("AWS_URL", "")
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_S3_FILE_OVERWRITE = True
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = "public-read"
