from qb.airports.models import Airport
from qb.elasticsearch import get_es_connection


async def handle_airport_search(request):
    q = request.json.get('meta').get('q')

    # Get ES Connection
    config = request.json.get('config')
    get_es_connection(config.get('elasticsearch').get('hosts'))

    Airport.init()

    results = await Airport.get_suggestions(search_phrase=q)

    return dict(data=results)