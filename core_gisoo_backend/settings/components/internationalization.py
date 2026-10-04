from decouple import config

LANGUAGE_CODE = config("LANGUAGE_CODE", "fa")
LANGUAGES = [
    ("fa", "فارسی"),
    ("en", "English"),
]
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_L10N = False
USE_TZ = True
