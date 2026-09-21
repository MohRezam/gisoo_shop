import os

from decouple import config

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# DEBUG defaults to False; only explicit true/1 enables it.
DEBUG = bool(str(config("DEBUG", default=False)).lower() in ["true", "1"])
TEST = bool(str(config("TEST", default=False)).lower() in ["true", "1"])
DISABLE_API_DOCS = bool(
    str(config("DISABLE_API_DOCS", default=False)).lower() in ["true", "1"]
)
