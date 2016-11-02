from sanic.exceptions import SanicException
from sanic.response import json
from qb.acta.errors import InvalidACTARequestError


class LagerError(SanicException):
    status_code = 500


class UnauthorizedError(SanicException):
    status_code = 401


def init_errors(app):
    @app.exception(LagerError)
    @app.exception(UnauthorizedError)
    @app.exception(InvalidACTARequestError)
    async def handle_error(request, exception):
        status_code = exception.status_code if hasattr(exception, 'status_code') else 500
        status_code = status_code if not isinstance(exception, InvalidACTARequestError) else 400

        response = {
            'status': status_code,
            'message': u'{}'.format(exception),
            'data': {}
        }
        return json(response,
                    status=status_code)