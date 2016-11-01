from qb.airports.models import Airport
from qb.elasticsearch import get_es_connection
import json
import objectpath


def process_airports(bulk):
	es = get_es_connection(hosts=['127.0.0.1'])

	with open('iata-airports.json') as f:
		count = 0

		iata_airports = json.loads(f.read())
		tiket_airports = bulk.get('all_flight')

		path = objectpath.Tree(iata_airports)

		Airport.init()

		for tiket_airport in tiket_airports:
			iata_airport = path.execute("$.airports[@.iata is '%s']" % tiket_airport.get('airport_code').upper())

			location = {}
			iata_country_code = ''
			for entry in iata_airport:
				location = dict(lat=entry.get('lat'), lon=entry.get('lon'))
				iata_country_code = entry.get('iso')
			if not location or not iata_country_code:
				continue
			if not location.get('lat') or not location.get('lon'):
				continue

			print('Airport: %s' % (tiket_airport.get('airport_code')))
			airport = Airport(name=tiket_airport.get('airport_name'),
							  area_name=tiket_airport.get('location_name'),
							  country=tiket_airport.get('country_name'),
							  iata_code=tiket_airport.get('airport_code'),
							  iata_country_code=iata_country_code,
							  location=location)
			airport.save()

			count += 1

		print('Got %d airports' % count)


with open('tiket-airport-list.json') as f:
	j = json.loads(f.read())
	process_airports(j)