import contextvars
import json
import logging
from datetime import datetime

_request_uid = contextvars.ContextVar("_request_uid", default="")


class StoreUidMiddleware:
    """Store uid in thread local var to be able to append it to logs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _request_uid.set(request.headers.get("x-uid", ""))

        response = self.get_response(request)
        return response


class RequestUIDFilter(logging.Filter):
    """Logging filter to inject request unique ID into log records."""

    def filter(self, record):
        record.request_uid = _request_uid.get()
        return True


class JsonFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return (
            datetime.fromtimestamp(record.created)
            .astimezone()
            .isoformat(timespec="milliseconds")
        )

    def format(self, record):
        record.message = record.getMessage()
        record.asctime = self.formatTime(record)
        json_record = {
            "datetime": record.asctime,
            "server": "noethysweb",
            "vhost": "sacadoc.flambeaux.org",
            "uid": record.request_uid,
            "message": record.message,
            "log_level": record.levelname,
            "pathname": record.pathname,
        }
        return json.dumps(json_record, ensure_ascii=False)
