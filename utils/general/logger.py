from datetime import datetime
import json
import logging


class Logger:
    print_in_console = True

    @classmethod
    def __log(cls, lvl, message, title):
        if cls.print_in_console:
            print(
                f"-------> {lvl}",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S+"),
                title,
                message,
                flush=True,
            )

    @classmethod
    def info(cls, logger=None, message=None, title="", additional_data=None):
        if additional_data is None:
            additional_data = {}

        cls.get_logger(logger).info(
            f"{title} {message}",
            extra={
                "title": title,
                "additional_data": json.dumps(
                    {
                        "type": additional_data.get("type", ""),
                        "view": additional_data.get("view", ""),
                        "method": additional_data.get("method", ""),
                        "url": additional_data.get("url", ""),
                        "params": additional_data.get("params", ""),
                        "user": additional_data.get("user", ""),
                        "size": additional_data.get("size", ""),
                        "error_info": additional_data.get("error_info", ""),
                        "extra": additional_data.get("extra", ""),
                        "referer": additional_data.get("referer", ""),
                        "user_agent": additional_data.get("user_agent", ""),
                        "status_code": additional_data.get("status_code", ""),
                        "host": additional_data.get("host", ""),
                        "origin": additional_data.get("origin", ""),
                        "source_ip": additional_data.get("source_ip", ""),
                        "response_time": additional_data.get("response_time", ""),
                    },
                    default=str,
                ),
            },
        )
        cls.__log("INFO", message, title)

    @classmethod
    def debug(cls, logger=None, message=None, title="", additional_data=None):
        if additional_data is None:
            additional_data = {}
        cls.get_logger(logger).warning(
            f"{title} {message}",
            extra={
                "title": title,
                "additional_data": json.dumps(
                    {
                        "type": additional_data.get("type", ""),
                        "view": additional_data.get("view", ""),
                        "method": additional_data.get("method", ""),
                        "url": additional_data.get("url", ""),
                        "params": additional_data.get("params", ""),
                        "user": additional_data.get("user", ""),
                        "size": additional_data.get("size", ""),
                        "error_info": additional_data.get("error_info", ""),
                        "extra": additional_data.get("extra", ""),
                        "referer": additional_data.get("referer", ""),
                        "user_agent": additional_data.get("user_agent", ""),
                        "status_code": additional_data.get("status_code", ""),
                        "host": additional_data.get("host", ""),
                        "origin": additional_data.get("origin", ""),
                        "source_ip": additional_data.get("source_ip", ""),
                        "response_time": additional_data.get("response_time", ""),
                    },
                    default=str,
                ),
            },
        )
        cls.__log("DEBUG", message, title)

    @classmethod
    def error(cls, logger=None, message=None, title="", additional_data=None):
        if additional_data is None:
            additional_data = {}
        cls.get_logger(logger).error(
            f"{title} {message}",
            extra={
                "title": title,
                "additional_data": json.dumps(
                    {
                        "type": additional_data.get("type", ""),
                        "view": additional_data.get("view", ""),
                        "method": additional_data.get("method", ""),
                        "url": additional_data.get("url", ""),
                        "params": additional_data.get("params", ""),
                        "user": additional_data.get("user", ""),
                        "size": additional_data.get("size", ""),
                        "error_info": additional_data.get("error_info", ""),
                        "extra": additional_data.get("extra", ""),
                        "referer": additional_data.get("referer", ""),
                        "user_agent": additional_data.get("user_agent", ""),
                        "status_code": additional_data.get("status_code", ""),
                        "host": additional_data.get("host", ""),
                        "origin": additional_data.get("origin", ""),
                        "source_ip": additional_data.get("source_ip", ""),
                        "response_time": additional_data.get("response_time", ""),
                    },
                    default=str,
                ),
            },
        )
        cls.__log("ERROR", message, title)

    @classmethod
    def get_logger(cls, logger) -> logging.Logger:
        if not logger:
            return logging.getLogger()
        return logger
