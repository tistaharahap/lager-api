from qb.flights.base import BaseFlightSearch
import requests


class TiketDotComFlightProvider(object):

    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def search(self, origin, destination, departure_date, **kwargs):
        parameters = self._build_search_parameters(origin, destination, departure_date, **kwargs)

        response = requests.get(self._build_url('/search/flight'),
                                params=parameters)
        
        return response.json()

    def update(self, **kwargs):
        
        return

    def _build_search_parameters(self, origin, destination, departure_date, **kwargs):
        parameters = {
            'd': origin,
            'a': destination,
            'date': departure_date,
            'token': self.token,
            'output': 'json'
        }

        parameters.update(kwargs)

        return parameters

    def _build_url(self, uri):
        return '%s%s' % (self.base_url, uri)


# BaseFlightSearch.register(TiketDotComFlightProvider)