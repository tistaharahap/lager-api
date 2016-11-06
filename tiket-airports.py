from qb.airports.models import Airport
from qb.elasticsearch import get_es_connection
import json
import objectpath
import requests


def get_geonames(city):
    url = u'http://api.geonames.org/wikipediaSearchJSON?q=%s&maxRows=10&username=tistaharahap' % (city)
    r = requests.get(url)

    results = r.json().get('geonames')
    if not results or len(results) == 0:
        return None

    return results[0]


def get_photo(city):
    search_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=%s&key=AIzaSyDgAOfmll7dUGJ3Et_NJN1MtUMJPitDD8c' % (city)
    r = requests.get(search_url)

    results = r.json().get('results')
    if not results:
        return ''

    photos = results[0].get('photos')
    if not photos or len(photos) == 0:
        return ''

    photo_ref = photos[0].get('photo_reference')
    if not photo_ref:
        return ''

    image_url = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=1200&photoreference=%s&key=AIzaSyDgAOfmll7dUGJ3Et_NJN1MtUMJPitDD8c' % photo_ref

    return image_url


def process_airports(tiket_airports):
    es = get_es_connection(hosts=['api.travelonbudget.co'])

    with open('iata-airports.json') as f:
        count = 0

        iata_airports = json.loads(f.read())
        curated_airports = []
        with open('curated-airports.json') as fc:
            curated_airports = json.loads(fc.read())

        path = objectpath.Tree(iata_airports)
        tiket_path = objectpath.Tree(tiket_airports)

        Airport.init()

        for tiket_airport in tiket_airports.get('all_flight'):
            tiket_airport_code = tiket_airport.get('airport_code')
            if not tiket_airport_code:
                continue

            iata_airport = path.execute("$.airports[@.iata is '%s']" % tiket_airport_code.upper())
            
            location = {}
            iata_country_code = ''
            for entry in iata_airport:
                location = dict(lat=entry.get('lat'), lon=entry.get('lon'))
                iata_country_code = entry.get('iso')

            if not location or not iata_country_code:
                continue
            if not location.get('lat') or not location.get('lon'):
                continue

            # Retrieve if existing
            existing_airport = Airport().search().query('match', iata_code=tiket_airport_code).execute()
            if len(existing_airport) == 1:
                existing_airport = existing_airport[0]

                if not hasattr(existing_airport, 'description') or existing_airport.description == '':
                    geonames = get_geonames(tiket_airport.get('location_name'))
                    existing_airport.update(description=geonames.get('summary') if geonames else '')

                if not hasattr(existing_airport, 'image') or existing_airport.image == '':
                    image = get_photo(tiket_airport.get('location_name'))
                    existing_airport.update(image=image)

                print(existing_airport.to_dict())

                continue

            geonames = get_geonames(tiket_airport.get('location_name'))
            image = get_photo(tiket_airport.get('location_name'))

            print('Airport: %s' % (tiket_airport.get('airport_code')))
            airport = Airport(name=tiket_airport.get('airport_name'),
                              area_name=tiket_airport.get('location_name'),
                              country=tiket_airport.get('country_name'),
                              iata_code=tiket_airport.get('airport_code'),
                              iata_country_code=iata_country_code,
                              location=location,
                              description=geonames.get('summary') if geonames else '',
                              wikipedia_url=geonames.get('wikipediaUrl') if geonames else '',
                              image=image)
            airport.save()

            print(airport.to_dict())

            count += 1

        # for airport in curated_airports:
        #     iata_airport = path.execute("$.airports[@.iata is '%s']" % airport.upper())
        #     tiket_airport = tiket_path.execute("$.all_flight[@.airport_code is '%s']" % airport.upper())

        #     location = {}
        #     iata_country_code = ''
        #     for entry in iata_airport:
        #         location = dict(lat=entry.get('lat'), lon=entry.get('lon'))
        #         iata_country_code = entry.get('iso')
        #     if not location or not iata_country_code:
        #         continue
        #     if not location.get('lat') or not location.get('lon'):
        #         continue

        #     for entry in tiket_airport:
        #         tiket_airport = entry
        #     if not tiket_airport:
        #         continue

        #     print('Airport: %s' % (tiket_airport.get('airport_code')))
        #     airport = Airport(name=tiket_airport.get('airport_name'),
        #                       area_name=tiket_airport.get('location_name'),
        #                       country=tiket_airport.get('country_name'),
        #                       iata_code=tiket_airport.get('airport_code'),
        #                       iata_country_code=iata_country_code,
        #                       location=location)
        #     airport.save()

        #     print(airport.to_dict())

        #     count += 1

        print('Got %d airports' % count)


with open('tiket-airport-list.json') as f:
    j = json.loads(f.read())
    process_airports(j)
