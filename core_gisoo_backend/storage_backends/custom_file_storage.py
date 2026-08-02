from urllib.parse import urljoin

from django.core.files.storage import FileSystemStorage
from django.utils.encoding import filepath_to_uri


class CustomFileStorage(FileSystemStorage):
    def url(self, name):
        if self.base_location is None:
            raise ValueError("This file is not accessible via a URL.")
        url = filepath_to_uri(name)
        if url is not None:
            url = url.lstrip("/")
        return urljoin(f"/{self.base_location}/", url)
