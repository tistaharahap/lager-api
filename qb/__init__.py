from sanic import Sanic
from qb.errors import init_errors, UnauthorizedError
from qb.auth import init_auth
from qb.responses import init_responses
from qb.acta import Verbs
from tiket import flight
import ujson


app = Sanic(__name__)
init_errors(app=app)
init_auth(app=app,
          error=UnauthorizedError)
init_responses(app=app)


TIKET_API_KEY = '210af2db93efbc0538b8c575e7f5cb2bb396dd31'

@app.route('/')
async def root(request):
    result = flight.search(TIKET_API_KEY,
                           origin='CGK',
                           destination='DPS',
                           date='2017-12-03',
                           ret_date='2017-12-05')

    return dict(data=result)


@app.route('/v1/events', methods=['POST', 'GET'])
async def acta(request):
    data = {
        "tickets": [],
        "contents": []
    }

    return dict(data=data)
