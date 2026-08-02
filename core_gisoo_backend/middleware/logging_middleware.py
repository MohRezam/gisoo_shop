import logging
import time

from utils.general.logger import Logger

logger = logging.getLogger("custom")


class ResponseLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        end_time = time.time()
        request_method = request.method
        user_id = (
            request.user.id if request.user and request.user.is_authenticated else None
        )
        url = request.path
        headers = dict(request.headers)
        source_ip = request.META.get("REMOTE_ADDR", None)
        response_time = float(round(end_time - start_time, 4))

        log_data = {
            "method": request_method,
            "user": user_id,
            "response_time": response_time,
            "source_ip": source_ip,
            "status_code": response.status_code,
            "url": url,
            "user_agent": headers.get("User-Agent"),
            "referer": headers.get("Referer"),
            "host": headers.get("Host"),
            "origin": headers.get("Origin"),
            "size": get_response_length(response),
        }
        Logger().info(
            logger,
            f"{request_method} {url} -> user_id {user_id}",
            title="Middleware-Logging-Requests",
            additional_data=log_data,
        )

        return response


def get_response_length(response):
    try:
        return len(response.content)
    except Exception:
        return 0
