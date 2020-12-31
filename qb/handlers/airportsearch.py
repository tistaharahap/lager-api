from qb.airports.models import Airport
from qb.elasticsearch import get_es_connection
from qb.flights.skyscanner.skyscanner import autocomplete_location


async def handle_airport_search(request):
    skyscanner_token = request.json.get('config').get('skyscanner').get('token')
    q = request.json.get('meta').get('q')

    results = await autocomplete_location(q=q,
                                          token=skyscanner_token)

    return dict(data=results)