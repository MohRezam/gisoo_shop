import json
import os

from decouple import config
from firebase_admin import credentials, initialize_app

from .constants import PROJECT_NAME

FCM_DJANGO_SETTINGS = {
    "APP_VERBOSE_NAME": f"{PROJECT_NAME} firebase",
    "FCM_SERVER_KEY": os.getenv("FIREBASE_API_KEY"),
}

json_cred = json.loads(config("GOOGLE_APPLICATION_CREDENTIALS", default="{}"))
if json_cred:
    cred = credentials.Certificate(json_cred)
    initialize_app(cred)
