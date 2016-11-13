from qb.airports.models import Airport
from qb.elasticsearch import get_es_connection
from qb.flights.skyscanner.skyscanner import search_flights, get_referral_link
from qb.flights.tiket.tiketdotcom import TiketDotComFlightProvider
import datetime
import pprint
import asyncio


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
        if not quote.get('airports').get('destination').get('iata_code'):
            quote['airports']['destination'] = normalize_airport(quote['airports']['destination'])
            quote['airports']['origin'] = normalize_airport(quote['airports']['origin'])

        try:
            quote['airports']['destination']['iata_code']
        except KeyError:
            quote['contents'] = {}
            continue

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


async def process_destination(departures, returns, skyscanner_token):
    departures = sorted(departures, key=lambda r: float(r.get('price_value')))
    returns = sorted(returns, key=lambda r: float(r.get('price_value')))

    departure = departures[0]
    returning = returns[0]

    destination = {
        'outbound': {
            'quote_id': 'not_from_skyscanner',
            'airline': departure.get('airlines_name')
        },
        'inbound': {
            'quote_id': 'not_from_skyscanner',
            'airline': returning.get('airlines_name')
        },
        'airports': {
            'origin': {
                'city_id': departure.get('departure_city'),
                'city_name': departure.get('departure_city_name'),
                'iata_code': departure.get('departure_city'),
                'country_name': 'not_from_skyscanner',
                'airport_name': departure.get('arrival_city_name')
            },
            'destination': {
                'city_id': returning.get('departure_city'),
                'city_name': returning.get('departure_city_name'),
                'iata_code': returning.get('departure_city'),
                'country_name': 'not_from_skyscanner',
                'airport_name': returning.get('arrival_city_name')
            }
        },
        'dates': {
            'outbound': departure.get('departure_flight_date').split(' ')[0],
            'inbound': returning.get('departure_flight_date').split(' ')[0]
        },
        'referral_link': get_referral_link(skyscanner_token, 
                                           departure.get('departure_city'), 
                                           returning.get('departure_city'), 
                                           departure.get('departure_flight_date').split(' ')[0], 
                                           returning.get('departure_flight_date').split(' ')[0]),
        'cheapest': int(float(departure.get('price_value'))) + int(float(returning.get('price_value')))
    }

    return destination


async def search_more_flights_within_budget(budget, quotes, token, base_url, skyscanner_token):
    if len(quotes) == 0:
        return quotes

    origin_airport = await get_origin_airport_from_quotes(quotes=quotes)
    if not origin_airport:
        return quotes

    print('Search more results for country: %s' % origin_airport.get('country'))

    if origin_airport.get('country') != 'Indonesia':
        return quotes

    destinations = [quote.get('airports').get('destination').get('IataCode') for quote in quotes]

    airports = await Airport.geosearch(location=origin_airport.get('location'),
                                       budget=budget)

    tiket = TiketDotComFlightProvider(base_url=base_url,
                                      token=token)
    departure_date = quotes[0].get('dates').get('outbound')
    returning_date = quotes[0].get('dates').get('inbound')

    for airport in airports:
        if airport.get('iata_code') in destinations:
            continue

        more_quotes = await tiket.search(origin=origin_airport.get('iata_code'),
                                         destination=airport.get('iata_code'),
                                         departure_date=departure_date,
                                         ret_date=returning_date,
                                         adult=1)
        # Oh tiket...
        asyncio.sleep(12)

        more_quotes = await tiket.search(origin=origin_airport.get('iata_code'),
                                         destination=airport.get('iata_code'),
                                         departure_date=departure_date,
                                         ret_date=returning_date,
                                         adult=1)
        if not more_quotes.get('departures'):
            continue
        if not more_quotes.get('returns'):
            continue

        quote = await process_destination(departures=more_quotes.get('departures').get('result'),
                                          returns=more_quotes.get('returns').get('result'),
                                          skyscanner_token=skyscanner_token)

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
                                                         token=config.get('tiketdotcom').get('token'),
                                                         base_url=config.get('tiketdotcom').get('base_url'),
                                                         skyscanner_token=config.get('skyscanner').get('token'))

    # Contents (picture, articles, etc)
    quotes = await get_content_for_quotes(quotes=quotes)

    # Filter & Sort
    quotes = await filter_quotes(budget=budget,
                                 quotes=quotes,
                                 min_percentage=33,
                                 max_percentage=120)

    return dict(data=quotes)


