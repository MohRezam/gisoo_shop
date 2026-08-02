import base64

from cryptography.fernet import Fernet
from django.conf import settings


def encrypt(raw_txt):
    """
    Function to encrypt raw text using Fernet class
    """
    try:
        txt = str(raw_txt)
        cipher_pass = Fernet(settings.ENCRYPTION_KEY)
        encrypted_text = cipher_pass.encrypt(txt.encode("ascii"))
        encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode("ascii")
        return encrypted_text
    except Exception:
        return None


def decrypt(encrypted_txt):
    """
    Function to decrypt encrypted text using Fernet class
    """
    try:
        txt = base64.urlsafe_b64decode(encrypted_txt)
        cipher_pass = Fernet(settings.ENCRYPTION_KEY)
        decoded_text = cipher_pass.decrypt(txt).decode("ascii")
        return decoded_text
    except Exception:
        return None
