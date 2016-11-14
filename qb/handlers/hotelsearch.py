from qb.elasticsearch import get_es_connection
from qb.airports.models import Airport
from qb.hotels.skyscanner.skyscanner import search_hotels


async def handle_hotel_search(request):
	meta = request.json.get('meta')

	checkin_date = meta.get('checkin_date')
	checkout_date = meta.get('checkout_date')
	airport_iata_code = meta.get('airport')

	get_es_connection(hosts=request.json.get('config').get('elasticsearch').get('hosts'))

	airport = await Airport.get_airport_by_iata_code(iata_code=airport_iata_code)
	location = airport.get('location')

	token = request.json.get('config').get('skyscanner').get('token')

	hotels = await search_hotels(token, checkin_date, checkout_date, location)

	return dict(data=hotels)