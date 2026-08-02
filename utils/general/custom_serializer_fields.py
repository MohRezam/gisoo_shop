# flake8: noqa
from base64 import b64encode
import mimetypes

from rest_framework import serializers
from rest_framework.settings import api_settings


class KeyChoiceField(serializers.ChoiceField):
    def to_representation(self, value):
        if value in self.choices.keys():
            return {"value": value, "text": self.choices[value]}
        return super().to_representation(value)


class WithUnitField(serializers.Field):
    def to_internal_value(self, data):
        if type(data) == dict:
            return data["value"], data["unit"]
        return data

    def to_representation(self, value):
        if type(value) == tuple:
            return {"value": value[0], "unit": value[1]}
        return super().to_representation(value)


def encode_b64(value, is_image=True):
    value.file.seek(0)
    data = value.file.read()
    if is_image:
        mime_type, encoding = mimetypes.guess_type(value.name)
        if not mime_type:
            mime_type = "image/png"
        file_data = bytes(
            "data:" + mime_type + ";base64,", encoding="UTF-8"
        ) + b64encode(data)
    else:
        file_data = b64encode(data)
    return file_data


class Base64ImageField(serializers.ImageField):
    def to_representation(self, value):
        return encode_b64(value)


class Base64FileField(serializers.FileField):
    def to_representation(self, value):
        return encode_b64(value, is_image=False)


CDN_URL = "sport-cdn.zarebin.ir"
OBJECT_STORAGE_URL = "cmn-prod-rgw.kp0.mci.dev"


class DynamicUrlImageField(serializers.ImageField):
    def to_representation(self, value):
        if not value:
            return None

        use_url = getattr(self, "use_url", api_settings.UPLOADED_FILES_USE_URL)
        if use_url:
            try:
                url = value.url
            except AttributeError:
                return None
            if any(
                value.name.startswith(protocol)
                for protocol in ("https://", "https%3A/")
            ):
                url = value.name.replace(OBJECT_STORAGE_URL, CDN_URL)
                return url
            request = self.context.get("request", None)
            if request is not None:
                url = request.build_absolute_uri(url)
            url = url.replace(OBJECT_STORAGE_URL, CDN_URL)
            return url

        return value.name
