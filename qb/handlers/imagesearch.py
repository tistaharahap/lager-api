from qb.elasticsearch import get_es_connection
from qb.airports.models import Airport
import redis
import requests
import json


def resolve_photo_for_bing(row):
    return {
        'url': row.get('contentUrl'),
        'attribution': row.get('hostPageUrl')
    }


async def handle_image_search(request):
    config = request.json.get('config')
    redis_config = config.get('redis')
    redis_conn = redis.StrictRedis(host=redis_config.get('host'),
                                   port=redis_config.get('port'),
                                   db=redis_config.get('db'))

    get_es_connection(hosts=config.get('elasticsearch').get('hosts'))

    meta = request.json.get('meta')
    if not meta:
        return []

    redis_key = 'image-search#%s' % meta.get('airport_iata_code')
    results = redis_conn.get(redis_key)
    if results:
        return dict(data=json.loads(str(results, 'utf-8')))

    airport = await Airport.get_airport_by_iata_code(iata_code=meta.get('airport_iata_code'))
    if not airport:
        return []

    q = airport.get('area_name')
    url = 'https://api.cognitive.microsoft.com/bing/v5.0/images/search?q=%s&count=20&offset=0&mkt=en-us&safeSearch=strict' % (q)
    headers = {
        'Ocp-Apim-Subscription-Key': '8fac5218b8d0448bbfbd07c72a3bbb61',
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    body = response.json()
    if not body:
        return []

    images = body.get('value')
    results = []
    for image in images:
        photo = resolve_photo_for_bing(image)
        if not photo.get('url'):
            continue

        results.append(photo)

    redis_conn.set(redis_key, json.dumps(results))
    return dict(data=results)
