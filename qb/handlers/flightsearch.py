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


async def get_origin_airport_from_quotes(quotes):
    if len(quotes) == 0:
        return None

    iata_code = quotes[0].get('airports').get('origin').get('IataCode')
    return await Airport.get_airport_by_iata_code(iata_code=iata_code)


async def search_more_flights_within_budget(budget, quotes, token, ip_address):
    if len(quotes) == 0:
        return quotes

    origin_airport = await get_origin_airport_from_quotes(quotes=quotes)
    if not origin_airport:
        return quotes

    destinations = [quote.get('airports').get('destination').get('IataCode') for quote in quotes]

    airports = await Airport.geosearch(location=origin_airport.get('location'),
                                       budget=budget)
    airports = filter(lambda a: a in destinations, airports)

    for airport in airports:
        more_quotes = await search_flights(token=token,
                                           origin=origin_airport.get('iata_code'),
                                           ip_address=ip_address,
                                           destination=airport.get('iata_code'),
                                           departure_date=quotes[0].get('dates').get('outbound'),
                                           returning_date=quotes[0].get('dates').get('inbound'),
                                           budget=budget)
        for quote in more_quotes:
            quotes.append(quote)

    return quotes


async def filter_quotes(budget, quotes, min_percentage=50, max_percentage=110):
    min_price = int(float(budget) * min_percentage / 100)
    max_price = int(float(budget) * max_percentage / 100)

    quotes = filter(lambda q: min_price <= q.get('cheapest') <= max_price, quotes)
    quotes = sorted(quotes, key=lambda q: q.get('cheapest'))

    return quotes


async def handle_flight_search_with_budget(request):
    meta = request.json.get('meta')

    budget = meta.get('number')

    origin = meta.get('origin')
    location = {
        'lat': origin.get('latitude') if origin else None,
        'lon': origin.get('longitude') if origin else None
    }
    ip_address = '%s-ip' % request.headers.get('X-Real-IP')
    
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

    # Do flight search
    quotes = await search_flights(token=config.get('skyscanner').get('token'),
                                  origin=location,
                                  ip_address=ip_address,
                                  destination='anywhere',
                                  departure_date=outbound_date,
                                  returning_date=inbound_date,
                                  budget=budget)

    # Widen search
    if len(quotes) > 0:
        quotes = await search_more_flights_within_budget(budget=budget,
                                                         quotes=quotes,
                                                         token=config.get('skyscanner').get('token'),
                                                         ip_address=ip_address)

    # Contents (picture, articles, etc)
    quotes = await get_content_for_quotes(quotes=quotes)

    # Filter & Sort
    quotes = await filter_quotes(budget=budget,
                                 quotes=quotes,
                                 min_percentage=33,
                                 max_percentage=120)

    return dict(data=quotes)


