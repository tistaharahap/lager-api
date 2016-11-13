
from qb.handlers.flightsearch import handle_flight_search_with_budget
from qb.handlers.airportsearch import handle_airport_search
from qb.handlers.attractionsearch import handle_attraction_search
from qb.handlers.routesearch import handle_route_search


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
    'route-search': {
        'actor': 'person',
        'object': 'route',
        'meta': {
            'required_fields': [
                'outbound_date',
                'inbound_date',
                'origin',
                'destination'
            ]
        }
    }
}
