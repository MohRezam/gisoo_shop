import logging.config
import os

from decouple import config

LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "[{asctime}] {levelname} {name}: {message}",
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": (
                    "{{"
                    '"time": "{asctime}", '
                    '"level": "{levelname}", '
                    '"logger": "{name}", '
                    '"message": "{message}", '
                    '"module": "{module}", '
                    '"func": "{funcName}", '
                    '"line": "{lineno}"'
                    "}}"
                ),
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "simple",
                "filename": os.path.join(LOG_DIR, "panel.log"),
            },
        },
        "loggers": {
            "": {
                "handlers": ["console", "file"],
                "level": "WARNING",
                "propagate": True,
            },
            "custom": {
                "handlers": (
                    ["console", "file"]
                    if config("LOGGING", default=True, cast=bool)
                    else ["console"]
                ),
                "level": "WARNING",
                "propagate": False,
            },
            "httpx": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "silk.model_factory": {
                "level": "CRITICAL",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "apps.items.tasks": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
)
