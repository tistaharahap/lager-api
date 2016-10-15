from sanic import Sanic
from sanic.response import json
from qb.errors.errors import init_errors, UnauthorizedError
import ujson


app = Sanic(__name__)
init_errors(app=app)


@app.middleware('request')
async def authorize_request(request):
    token = request.headers.get('X-Access-Token')
    if not token:
        raise UnauthorizedError('All requests must be set with X-Access-Token header')


@app.middleware('response')
async def format_response(request, response):
    status = response.get('status')
    status = status if status else 200
    
    message = response.get('message')
    message = message if message else ''

    headers = response.get('headers')

    data = response.get('data')

    response = {
        'status': status,
        'message': message,
        'data': data
    }

    return json(response, 
                status=status,
                headers=headers)


@app.route('/')
async def root(request):
    return dict(data={'hello': 'world'},
                message='ok',
                status=200)


@app.route('/v1/events', methods=['GET', 'POST'])
async def acta(request):
    data = {
        "actor": {
            "id": "8f07dc44-df69-4e31-9ad9-c2002d95f68a",
            "kind": "place"
        },
        "action": "query-result",
        "object": {
            "id": "2fe614af-266b-4773-a066-3b518763380b",
            "kind": "person"
        },
        "meta": {
            "coordinates": {
                "latitude": -6.1273181,
                "longitude": 106.123123
            },
            "tickets": [
                {}
            ],
            "contents": {}
        }
    }

    return dict(data=data)