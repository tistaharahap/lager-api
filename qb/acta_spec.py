
from qb.handlers.flightsearch import handle_flight_search_with_budget


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
