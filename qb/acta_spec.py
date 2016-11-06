
from qb.handlers.flightsearch import handle_flight_search_with_budget
from qb.handlers.airportsearch import handle_airport_search


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
                'dates',
                'passengers'
            ]
        },
        'handler': handle_flight_search_with_budget
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
