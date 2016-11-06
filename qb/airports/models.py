from elasticsearch_dsl import DocType, String, Date, Boolean, GeoPoint, analyzer
from datetime import datetime


class Airport(DocType):
    name = String(analyzer='snowball')
    area_name = String(analyzer='snowball')
    country = String(analyzer='snowball')

    iata_code = String(analyzer='snowball')
    iata_country_code = String(analyzer='snowball')

    location = GeoPoint(lat_lon=True)

    class Meta:
        doc_type = 'airport'
        index = 'airports'

    async def save(self, **kwargs):
        self.created_at = datetime.now()
        return super().save(**kwargs)

    @classmethod
    async def get_suggestions(cls, search_phrase):
        term = {
            'field': 'area_name'
        }
        results = Airport().search().suggest('airport_suggestions', search_phrase, term=term).execute()

        return [result.to_dict() for result in results]

    @classmethod
    async def get_nearest_airport(cls, location):
        sorter = {
            '_geo_distance': {
                'location': location,
                'order': 'asc',
                'unit': 'km'
            }
        }

        results = Airport().search().sort(sorter).execute()

        return results[0].to_dict()

    @classmethod
    async def geosearch(cls, location, budget):
        distances = get_distances_from_budget(budget=budget)

        filter_args = {
            'from': '{}m'.format(distances[0] * 1000),
            'to': '{}m'.format(distances[1] * 1000),
            'location': location
        }

        results = Airport().search().filter('geo_distance_range', **filter_args).execute()
        
        return [row.to_dict() for row in results]


def get_distances_from_budget(budget):
    budget = int(budget)
    distances = (100, 1000)

    if 1500000 < budget <= 3500000:
        distances = (1000, 3000)
    elif 3500000 < budget <= 5000000:
        distances = (3000, 4000)
    elif 5000000 < budget < 8000000:
        distances = (4000, 8000)
    elif budget > 8000000:
        distances = (8000, 15000)

    return distances
