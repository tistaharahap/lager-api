from qb.articles import Article
from qb.flights.tiket import TiketDotComFlightProvider
from qb.airports.models import Airport
from qb.elasticsearch import get_es_connection
from operator import itemgetter
import datetime
import asyncio


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

    return (next_friday, next_sunday)


async def get_destination_fares(origin_airport, destination_airport, dates, passengers, tiketdotcom_provider):
    result = await tiketdotcom_provider.search(origin=origin_airport,
                                               destination=destination_airport,
                                               departure_date=dates.get('outbound'),
                                               ret_date=dates.get('inbound'),
                                               adult=passengers.get('adults'))
    
    # Hey Tiket, you could design a better API?
    asyncio.sleep(10)

    result = await tiketdotcom_provider.search(origin=origin_airport,
                                               destination=destination_airport,
                                               departure_date=dates.get('outbound'),
                                               ret_date=dates.get('inbound'),
                                               adult=passengers.get('adults'))

    return result


async def parse_destinations(origin_airport, airports, dates, passengers, budget, tiketdotcom_provider):
    result = []

    outbound_date = dates.get('outbound')
    inbound_date = dates.get('inbound')

    def _assign_flight(row):
        return {
            'id': row.get('flight_id'),
            'airline': {
                'name': row.get('airlines_name'),
                'flight_number': row.get('flight_number'),
                'picture': row.get('image')
            },
            'prices': {
                'adult': int(float(row.get('price_adult'))),
                'child': int(float(row.get('price_child'))),
                'infant': int(float(row.get('price_infant')))
            },
            'baggage': {
                'unit': row.get('check_in_baggage_unit'),
                'value': row.get('check_in_baggage')
            },
            'datetime': {
                'departure': row.get('departure_flight_date'),
                'arrival': row.get('arrival_flight_date')
            }
        }

    def _format_fares(departures, returns):
        departures = sorted([_assign_flight(row) for row in departures.get('result')], key=lambda e: e['prices']['adult'])
        returns = sorted([_assign_flight(row) for row in returns.get('result')], key=lambda e: e['prices']['adult'])
        
        return (departures, returns)

    def _get_content_from_destination(airport):
        return {
            'picture': 'https://static1.squarespace.com/static/5372cd85e4b0bbcc0ca2de9d/53ed02f9e4b0b7e18f4b62eb/53ee694fe4b032360e1f74d5/1408133521826/04-Gili-Trawangan-Lombok-Hotel-Rooms-Facilities-Beach-Beachfront-Ocean-Sun-Chair-White-Sand.jpg?format=2500w',
            'title': '[STUB] Title',
            'destination': '[STUB] Destination',
            'area': airport.get('area_name'),
            'article': {
                'author': '[STUB] Aria Rajasa',
                'body': '[STUB] Article body',
                'coordinates': {
                    'latitude': 0.0,
                    'longitude': 0.0
                }
            }
        }

    for airport in airports:
        iata_code = airport.get('iata_code')

        fares = await get_destination_fares(origin_airport=origin_airport.get('iata_code'),
                                            destination_airport=iata_code,
                                            dates=dates,
                                            passengers=passengers,
                                            tiketdotcom_provider=tiketdotcom_provider)
        
        departures = fares.get('departures')
        returns = fares.get('returns')
        if not departures or not returns:
            continue

        outbound = []
        inbound = []
        content = _get_content_from_destination(airport=airport)

        (outbound, inbound) = _format_fares(departures, returns)
        airports = {
            'origin': origin_airport,
            'destination': airport
        }

        result.append({
            'contents': content,
            'outbound': outbound,
            'inbound': inbound,
            'airports': airports
        })

    # Filter out prices that are more than 20% in excess or less
    #result = filter(lambda row: int(float(budget) * 0.7) <= row.get('price_total') <= int(float(budget) * 1.2), result)

    return result


async def handle_flight_search_with_budget(request):
    meta = request.json.get('meta')

    budget = meta.get('number')
    location = {
        'lat': meta.get('origin').get('latitude'),
        'lon': meta.get('origin').get('longitude')
    }
    
    dates = meta.get('dates')
    passengers = meta.get('passengers')

    config = request.json.get('config')

    # Get ES Connection
    get_es_connection(config.get('elasticsearch').get('hosts'))

    # Nearest Airport for Origin
    origin_airport = await Airport.get_nearest_airport(location=location)

    # Get destination airports
    airports = await Airport.geosearch(location=location,
                                       budget=budget)

    tiketdotcom_provider = TiketDotComFlightProvider(base_url=config.get('tiketdotcom').get('base_url'),
                                                     token=config.get('tiketdotcom').get('token'))

    destinations = await parse_destinations(origin_airport=origin_airport,
                                            airports=airports,
                                            dates=dates,
                                            passengers=passengers,
                                            budget=budget,
                                            tiketdotcom_provider=tiketdotcom_provider)

    return dict(data=destinations)


