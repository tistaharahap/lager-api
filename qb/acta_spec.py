
from qb.handlers.flightsearch import handle_flight_search_with_budget
from qb.handlers.airportsearch import handle_airport_search
from qb.handlers.attractionsearch import handle_attraction_search


async def handle_bookmark_destination(request):
    pass


Verbs = {
    'flight-search-with-budget': {
        'actor': 'person',
        'object': 'currency-number',
        'meta': {
            'required_fields': [
                'currency',
                'number',
                'origin',
                'passengers'
            ]
        },
        'handler': handle_flight_search_with_budget
    },
    'search-for-attractions': {
        'actor': 'person',
        'object': 'attractions',
        'meta': {
            'required_fields': [
                'latitude',
                'longitude'
            ]
        },
        'handler': handle_attraction_search
    },
    'airport-search': {
        'actor': 'person',
        'object': 'search-phrase',
        'meta': {
            'required_fields': [
                'q'
            ]
        },
        'handler': handle_airport_search
    },
    'bookmark-destination': {
        'actor': 'person',
        'object': 'destination',
        'meta': {
            'required_fields': [
                'destination'
            ]
        },
        'handler': handle_bookmark_destination
    }
}
