from core_gisoo_backend.storage_backends import MediaStorage
from core_gisoo_backend.storage_backends.media_storage import BASE_MEDIA_LOCATION

def avatar_path():
    return f"{BASE_MEDIA_LOCATION}/users/avatars"


