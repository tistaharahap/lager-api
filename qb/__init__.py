from sanic import Sanic
from qb.errors import init_errors, UnauthorizedError
from qb.auth import init_auth
from qb.responses import init_responses
from qb.acta import Verbs
from qb.articles import get_es_connection, Article
import ujson


app = Sanic(__name__)
init_errors(app=app)
init_auth(app=app,
          error=UnauthorizedError)
init_responses(app=app)


TIKET_API_KEY = '210af2db93efbc0538b8c575e7f5cb2bb396dd31'
ES_HOSTS = ['192.168.99.100']

@app.route('/')
@app.route('/v1')
async def root(request):
    return dict(data=None)


@app.route('/v1/flight-search', methods=['POST'])
async def acta(request):
    data = {
        "outbound": [],
        "inbound": [],
        "contents": []
    }

    es_conn = get_es_connection(hosts=ES_HOSTS)
    results = Article.geosearch(location=dict(lat=-6.123981, lon=106.123123))
    
    print(results)

    return dict(data=data)
