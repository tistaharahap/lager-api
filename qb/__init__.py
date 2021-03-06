from sanic import Sanic
from qb.errors import init_errors, UnauthorizedError
from qb.auth import init_auth
from qb.responses import init_responses
from qb.acta import validate_request, InvalidACTARequestError
from qb.acta_spec import Verbs


app = Sanic(__name__)
init_errors(app=app)
init_auth(app=app,
          error=UnauthorizedError)
init_responses(app=app)

TIKET_API_KEY = '210af2db93efbc0538b8c575e7f5cb2bb396dd31'
TIKET_BASE_URL = 'http://api-sandbox.tiket.com'

SKYSCANNER_TOKEN = 'ba842744824325399712479687403277'

ES_HOSTS = ['api.travelonbudget.co']

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 7

print('Serving lager..')

# No globals in Sanic, injecting this to every request
g = {
    'config': {
        'tiketdotcom': {
            'token': TIKET_API_KEY,
            'base_url': TIKET_BASE_URL
        },
        'skyscanner': {
            'token': SKYSCANNER_TOKEN
        },
        'elasticsearch': {
            'hosts': ES_HOSTS
        },
        'redis': {
            'host': REDIS_HOST,
            'port': REDIS_PORT,
            'db': REDIS_DB
        }
    }
}

@app.route('/')
@app.route('/v1')
async def root(request):
    return dict(data=None)


@app.route('/v1/events', methods=['POST'])
async def acta(request):
    if not request.json:
        raise InvalidACTARequestError('Empty request body')

    verb = request.json.get('action')
    handler = await validate_request(spec=Verbs.get(verb), 
                                     request=request.json)

    # Inject globals
    request.json.update(g)

    return await handler(request)
