from datetime import datetime

from gunicorn import glogging

class Logger(glogging.Logger):
    def atoms(self, resp, req, environ, request_time):
        atoms = super().atoms(resp, req, environ, request_time)
        # Approx request start based on request time
        request_start = datetime.now().astimezone() - request_time
        atoms["{request_start}c"] = request_start.isoformat(timespec="milliseconds")
        return atoms
