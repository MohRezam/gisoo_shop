from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class NotEqualObjectsException(Exception):
    pass


class BaseAPITestCase(APITestCase):
    serializer_map: dict

    def check_serializer_format(self, data: dict):
        self._assertObjectKeysEqual(self.serializer_map, data)

    def _assertObjectKeysEqual(self, data_format, data):
        if not data:
            return
        if isinstance(data_format, list):
            assert isinstance(data, list)
            for k1 in data:
                self._assertObjectKeysEqual(data_format[0], k1)
        else:
            for k1 in data_format.keys():
                if k1 not in data.keys():
                    raise NotEqualObjectsException()
                if isinstance(data_format[k1], dict):
                    self._assertObjectKeysEqual(data_format[k1], data[k1])
            if set(data_format.keys()) != set(data.keys()):
                raise NotEqualObjectsException()


class CustomAPITestCase(BaseAPITestCase):
    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
        }

    def jwt_authenticate_user(self, user, jwt_access_token):
        self.client.force_authenticate(user, jwt_access_token)
