from elasticsearch_dsl import DocType, String, Date, Boolean, GeoPoint, analyzer, Completion
from datetime import datetime


class Airport(DocType):
    name = String(analyzer='snowball')
    area_name = String(analyzer='snowball')
    country = String(analyzer='snowball')

    iata_code = String(analyzer='snowball')
    iata_country_code = String(analyzer='snowball')

    location = GeoPoint(lat_lon=True)

    description = String(analyzer='snowball')
    wikipedia_url = String(analyzer='snowball')

    image = String(analyzer='snowball')

    area_name_suggest = Completion(payloads=True)

    last_search_without_hit = Boolean()

    class Meta:
        doc_type = 'airport'
        index = 'airports'

    def save(self, **kwargs):
        self.created_at = datetime.now()
        return super().save(**kwargs)

    @classmethod
    async def get_airport_by_iata_code(cls, iata_code, to_dict=True):
        results = Airport().search().query('match', iata_code=iata_code).execute()
        if not results:
            return None

        return results[0].to_dict() if to_dict else results[0]

    @classmethod
    async def get_suggestions(cls, search_phrase):
        term = {
            'field': 'area_name_suggest'
        }
        results = Airport().search().suggest('airport_suggestions', search_phrase, completion=term).execute()

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
        if not results:
            return None

        return results[0].to_dict()

    @classmethod
    async def geosearch(cls, location, budget):
        distances = get_distances_from_budget(budget=budget)

        filter_args = {
            'from': '{}km'.format(distances[0]),
            'to': '{}km'.format(distances[1]),
            'location': location
        }

        results = Airport().search().query('match', last_search_without_hit=False).filter('geo_distance_range', **filter_args).scan()
        
        return [row.to_dict() for row in results]


def get_distances_from_budget(budget):
    budget = int(budget)
    distances = (100, 1000)

    if 0 < budget <= 1500000:
        distances = (100, 1000)
    elif 1500000 < budget <= 2000000:
        distances = (800, 1250)
    elif 2000000 < budget <= 3000000:
        distances = (1000, 1750)
    elif 3000000 < budget <= 4000000:
        distances = (1500, 2250)
    elif 4000000 < budget <= 5000000:
        distances = (2000, 2750)
    elif 5000000 < budget <= 6000000:
        distances = (2500, 3250)
    elif 6000000 < budget <= 7000000:
        distances = (3000, 3750)
    else:
        distances = (3500, 15000)

    return distances
