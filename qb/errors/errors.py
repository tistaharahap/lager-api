from sanic.exceptions import SanicException
from sanic.response import json


class LagerError(SanicException):
    status_code = 500


class UnauthorizedError(SanicException):
    status_code = 401


def init_errors(app):
    @app.exception(UnauthorizedError)
    def handle_error(request, exception):
        response = {
            'status': exception.status_code,
            'message': u'{}'.format(exception),
            'data': {}
        }
        return json(response,
                    status=exception.status_code)