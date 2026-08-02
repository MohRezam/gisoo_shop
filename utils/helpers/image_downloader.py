from io import BytesIO
import uuid

from django.utils.timezone import now
import requests


def download_image_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image_bytes = BytesIO(response.content)
            return image_bytes
        else:
            return None
    except requests.exceptions.RequestException:
        return None


def generate_unique_image_name(filename=None):
    if not filename:
        filename = "default_image"
    short_uuid = str(uuid.uuid4())[:6]
    unique_name = (
        f"{filename[:20]}_{now().strftime('%Y-%m-%d-%H-%M-%S')}_{short_uuid}.jpg"
    )
    return unique_name
