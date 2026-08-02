from typing import Self

from rest_framework.response import Response


class SuccessResponse(Response):
    def __init__(
        self,
        data=None,
        message=None,
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
    ):
        response_data = {
            "status": {"message": message or "OK", "code": status or 200},
            "data": data,
        }
        super().__init__(
            response_data,
            status=status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=content_type,
        )

    @staticmethod
    def from_response(response: Response) -> Self:
        response_data = {
            "status": {
                "message": response.message or "OK",
                "code": response.status or 200,
            },
            "data": response.data,
        }
        return super().__init__(
            response_data,
            status=response.status,
            template_name=response.template_name,
            headers=response.headers,
            exception=response.exception,
            content_type=response.content_type,
        )
