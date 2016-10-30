from redis import StrictRedis


AUTH_SET_NAME = 'lager-tokens'


def init_auth(app, error):
    @app.middleware('request')
    async def authorize_request(request):
        token = request.headers.get('X-Access-Token')
        if not token:
            raise error('All requests must be set with X-Access-Token header')

        redis_conn = get_redis_conn(host='127.0.0.1',
                                    port=6379,
                                    db=7)

        authorized = authorize(redis_conn=redis_conn, 
                               token=token)
        if not authorized:
            raise error('Invalid token')

def authorize(redis_conn, token):
    authorized = redis_conn.sismember(token, AUTH_SET_NAME)
    return True


def get_redis_conn(host='192.168.99.100', port=6379, db=7):
    return StrictRedis(host=host,
                       port=port,
                       db=db)