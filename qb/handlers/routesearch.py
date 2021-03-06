from qb.flights.tiket.tiketweb import search_flights
from qb.flights.skyscanner.skyscanner import get_referral_link
from qb.airports.models import Airport
from qb.elasticsearch import get_es_connection


async def handle_route_search(request):
    config = request.json.get('config')
    get_es_connection(hosts=config.get('elasticsearch').get('hosts'))
    skyscanner_token = config.get('skyscanner').get('token')

    meta = request.json.get('meta')

    origin_airport = await Airport.get_airport_by_iata_code(iata_code=meta.get('origin'))
    destination_airport = await Airport.get_airport_by_iata_code(iata_code=meta.get('destination'))
    outbound_date = meta.get('outbound_date')
    inbound_date = meta.get('inbound_date')

    flight = await search_flights(origin=origin_airport,
                                  destination=destination_airport,
                                  departure_date=outbound_date,
                                  returning_date=inbound_date,
                                  skyscanner_token=skyscanner_token)
    
    flight.update({
        'contents': {
            'picture': destination_airport.get('image') if destination_airport else '',
            'description': destination_airport.get('description') if destination_airport else '',
            'wikipedia_url': 'http://%s' % destination_airport.get('wikipedia_url') if destination_airport else '',
            'location': destination_airport.get('location')
        }
    })

    return dict(data=flight)