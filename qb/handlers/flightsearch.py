from qb.airports.models import Airport
from qb.elasticsearch import get_es_connection
from qb.flights.skyscanner.skyscanner import search_flights
import datetime


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


async def handle_flight_search_with_budget(request):
    meta = request.json.get('meta')

    budget = meta.get('number')
    location = {
        'lat': meta.get('origin').get('latitude'),
        'lon': meta.get('origin').get('longitude')
    }
    
    dates = meta.get('dates')
    try:
        outbound_date = dates.get('outbound')
        inbound_date = dates.get('inbound')
    except AttributeError:
        (outbound_date, inbound_date) = get_next_weekend()

    config = request.json.get('config')

    # Get ES Connection
    get_es_connection(config.get('elasticsearch').get('hosts'))

    # Nearest Airport for Origin
    origin_airport = await Airport.get_nearest_airport(location=location)

    quotes = await search_flights(token=config.get('skyscanner').get('token'),
                                  origin=origin_airport,
                                  destination='anywhere',
                                  departure_date=outbound_date,
                                  returning_date=inbound_date,
                                  budget=budget)

    return dict(data=quotes)


