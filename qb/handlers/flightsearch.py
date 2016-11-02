from qb.articles import Article
from qb.flights.tiket import TiketDotComFlightProvider
from qb.airports.models import Airport
from qb.elasticsearch import get_es_connection


async def handle_flight_search_with_budget(request):
	meta = request.json.get('meta')

	budget = meta.get('number')
	location = {
		'lat': meta.get('origin').get('latitude'),
		'lon': meta.get('origin').get('longitude')
	}
	print(location)
	dates = meta.get('dates')
	passengers = meta.get('passengers')

	config = request.json.get('config')

	# Get ES Connection
	get_es_connection(config.get('elasticsearch').get('hosts'))

	airports = Airport.geosearch(location=location,
								 budget=budget)

	tiketdotcom_provider = TiketDotComFlightProvider(base_url=config.get('tiketdotcom').get('base_url'),
													 token=config.get('tiketdotcom').get('token'))

	return dict(data=airports)