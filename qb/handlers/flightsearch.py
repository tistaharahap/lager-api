from qb.airports.models import Airport
from qb.elasticsearch import get_es_connection
from qb.flights.skyscanner.skyscanner import search_flights
import datetime
import pprint


pp = pprint.PrettyPrinter(indent=4)


def get_next_weekend():
    today = datetime.date.today()
    weekday = today.weekday()

    next_friday = None

    if 0 <= weekday <= 3:
        next_friday = today + datetime.timedelta(4 - weekday)
    elif weekday == 4:
        next_friday = today + datetime.timedelta(7)
    elif 4 < weekday < 7:
        next_friday = today + datetime.timedelta(7) - datetime.timedelta(weekday - 4)

    next_sunday = next_friday + datetime.timedelta(2)

    return (str(next_friday), str(next_sunday))


def normalize_airport(airport):
    return {
        'country_name': airport.get('CountryName'),
        'city_id': airport.get('CityId'),
        'city_name': airport.get('CityName'),
        'iata_code': airport.get('IataCode'),
        'airport_name': airport.get('Name')
    }


async def get_content_for_quotes(quotes):
    for quote in quotes:
        quote['airports']['destination'] = normalize_airport(quote['airports']['destination'])
        quote['airports']['origin'] = normalize_airport(quote['airports']['origin'])

        destination = await Airport.get_airport_by_iata_code(iata_code=quote['airports']['destination']['iata_code'])
        if not destination:
            quote['contents'] = {}
            continue
        
        quote['contents'] = {
            'picture': destination.get('image') if destination else '',
            'description': destination.get('description') if destination else '',
            'wikipedia_url': 'http://%s' % destination.get('wikipedia_url') if destination else '',
            'location': destination.get('location')
        }

    return quotes


async def handle_flight_search_with_budget(request):
    meta = request.json.get('meta')

    budget = meta.get('number')

    origin = meta.get('origin')
    location = {
        'lat': origin.get('latitude') if origin else None,
        'lon': origin.get('longitude') if origin else None
    }
    
    dates = meta.get('dates')
    try:
        outbound_date = dates.get('outbound')
        inbound_date = dates.get('inbound')
        if not outbound_date or not inbound_date:
            (outbound_date, inbound_date) = get_next_weekend()
    except AttributeError:
        (outbound_date, inbound_date) = get_next_weekend()

    config = request.json.get('config')

    # Get ES Connection
    get_es_connection(config.get('elasticsearch').get('hosts'))

    ip_address = '%s-ip' % request.headers.get('Remote-Addr').split(':')[0]
    print('Requesting IP Address: %s' % ip_address)
    quotes = await search_flights(token=config.get('skyscanner').get('token'),
                                  origin=ip_address,
                                  destination='anywhere',
                                  departure_date=outbound_date,
                                  returning_date=inbound_date,
                                  budget=budget)
    quotes = await get_content_for_quotes(quotes=quotes)

    return dict(data=quotes)


