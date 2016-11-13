from qb.airports.models import Airport
from qb.elasticsearch import get_es_connection


get_es_connection(hosts=['travelonbudget.co'])

for airport in Airport.search().query().scan():
	airport.update(last_search_without_hit=False)