import os

from .common import DEBUG

base_add_server_test = os.getenv("SERVER_TEST_URL", "")
base_add_server = os.getenv("SERVER_URL", "")


def get_server_add():
    return base_add_server if not DEBUG else base_add_server_test
