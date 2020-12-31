from qb.acta.errors import InvalidACTARequestError, InvalidACTAHandlerError
from voluptuous import Schema, Invalid, MultipleInvalid


def _validate_is_callable(obj):
    is_callable = hasattr(obj, '__call__')
    if not is_callable:
        raise Invalid('The request handler must be a callable')

    return obj


request_schema = Schema({
    'actor': str,
    'object': str,
    'meta': dict,
    'handler': _validate_is_callable
})


async def validate_request(spec, request):
    try:
        request_schema(spec)
    except MultipleInvalid as e:
        raise InvalidACTARequestError(str(e))

    return spec.get('handler')