import requests


def normalize_places(place):
    return {
        'skyscanner_place_id': place.get('PlaceId'),
        'skyscanner_country_id': place.get('CountryId'),
        'name': place.get('PlaceName'),
        'country': place.get('CountryName')
    }


async def autocomplete_location(token, q, market='ID', currency='IDR', locale='en-US'):
    url = 'http://partners.api.skyscanner.net/apiservices/autosuggest/v1.0/{}/{}/{}/?query={}&apiKey={}'
    url = url.format(market, currency, locale, q, token)

    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    results = response.json()
    if not results:
        return []

    return [normalize_places(row) for row in results.get('Places')]


async def find_carrier(carrier_id, carriers):
    for carrier in carriers:
        if carrier.get('CarrierId') == carrier_id:
            return carrier


async def find_destination(dest_id, places):
    for place in places:
        if int(place.get('PlaceId')) == int(dest_id):
            return place


def get_referral_link(token, origin, destination, departure_date, returning_date):
    return 'http://partners.api.skyscanner.net/apiservices/referral/v1.0/ID/IDR/en-US/%s/%s/%s/%s?apiKey=%s' % (origin, destination, departure_date, returning_date, token) 


async def process_quote(quote, carriers, places, departure_date, returning_date, token, origin):
    outbound_leg = quote.get('OutboundLeg')
    if not outbound_leg:
        return None

    inbound_leg = quote.get('InboundLeg')
    if not inbound_leg:
        return None

    outbound_carrier_ids = outbound_leg.get('CarrierIds')
    if not outbound_carrier_ids:
        return None

    inbound_carrier_ids = inbound_leg.get('CarrierIds')
    if not inbound_carrier_ids:
        return None

    outbound_carrier = await find_carrier(outbound_carrier_ids[0], carriers)
    inbound_carrier = await find_carrier(inbound_carrier_ids[0], carriers)

    origin_airport = inbound_leg.get('DestinationId')
    origin_airport = await find_destination(origin_airport, places)

    destination_airport = outbound_leg.get('DestinationId')
    destination_airport = await find_destination(destination_airport, places)

    destination = {
        'outbound': {
            'quote_id': quote.get('QuoteId'),
            'airline': outbound_carrier.get('Name')
        },
        'inbound': {
            'quote_id': quote.get('QuoteId'),
            'airline': inbound_carrier.get('Name')
        },
        'airports': {
            'origin': origin_airport,
            'destination': destination_airport
        },
        'dates': {
            'outbound': departure_date,
            'inbound': returning_date
        },
        'referral_link': get_referral_link(token, origin, destination_airport.get('IataCode'), departure_date, returning_date),
        'cheapest': quote.get('MinPrice')
    }

    return destination


def filter_quotes(budget, quotes, min_percentage=50, max_percentage=150):
    min_price = int(float(budget) * min_percentage / 100)
    max_price = int(float(budget) * max_percentage / 100)

    return filter(lambda q: min_price <= q.get('MinPrice') <= max_price, quotes)


async def search_flights(token, origin, ip_address, destination, departure_date, returning_date, budget, market='ID', currency='IDR', language='en-US'):
    if not origin or not origin.get('lat') or not origin.get('lon'):
        origin = ip_address
    else:
        origin = '%s,%s-Latlong' % (origin.get('lat'), origin.get('lon'))

    url = 'http://partners.api.skyscanner.net/apiservices/browsequotes/v1.0/ID/IDR/en-US/%s/%s/%s/%s?apiKey=%s' % (origin, destination, departure_date, returning_date, token)

    headers = {
        'Accept': 'application/json'
    }

    request = requests.get(url, headers=headers)
    json = request.json()
    if not json:
        return []

    quotes = json.get('Quotes')
    if not quotes:
        return []
        
    quotes = sorted(quotes, key=lambda e: e.get('MinPrice'))

    # Filter
    json['Quotes'] = filter_quotes(budget=budget, 
                                   quotes=quotes,
                                   min_percentage=30,
                                   max_percentage=130)

    carriers = json.get('Carriers')
    places = json.get('Places')

    destinations = []

    for quote in quotes:
        destination = await process_quote(quote=quote,
                                          carriers=carriers,
                                          places=places,
                                          returning_date=returning_date,
                                          departure_date=departure_date,
                                          token=token,
                                          origin=origin)

        if destination:
            destinations.append(destination)
    
    return destinations