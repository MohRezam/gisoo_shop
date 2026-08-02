from rest_framework.exceptions import APIException


class ServiceUnAvailable(APIException):
    status_code = 500
    default_detail = "Service temporarily unavailable, try again later."
    default_code = "service_unavailable"


class BadRequestInput(APIException):
    status_code = 400
    default_detail = "check your inputs"
    default_code = "wrong input"


class FailedDependency(APIException):
    status_code = 424
    default_detail = "مشکلی رخ داده است دوباره تلاش کنید"


class NotValidData(APIException):
    status_code = 406
    default_detail = "data is not valid"


class NotFound(APIException):
    status_code = 404
    default_detail = "Not Found :😭"


class NotAllow(APIException):
    status_code = 405
    default_detail = "you'r not allow this"
