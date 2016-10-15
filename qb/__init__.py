from sanic import Sanic
from qb.errors import init_errors, UnauthorizedError
from qb.auth import init_auth
from qb.responses import init_responses
import ujson


app = Sanic(__name__)
init_errors(app=app)
init_auth(app=app,
          error=UnauthorizedError)
init_responses(app=app)


@app.route('/')
async def root(request):
    return dict(data={'hello': 'world'})


@app.route('/v1/events', methods=['POST', 'GET'])
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