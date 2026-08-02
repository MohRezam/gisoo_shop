import os

from decouple import config

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Set the Django setting from the environment variable.
DEBUG = bool(str(config("DEBUG", default=True)).lower() in ["true", "1"])
TEST = bool(str(config("TEST", default=False)).lower() in ["true", "1"])
