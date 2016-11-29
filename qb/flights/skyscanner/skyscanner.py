import requests
import pprint

pp = pprint.PrettyPrinter(indent=2)


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


def get_referral_link(token, origin, destination, departure_date, returning_date, market='ID', currency='IDR', language='en-US'):
    return 'http://partners.api.skyscanner.net/apiservices/referral/v1.0/%s/%s/%s/%s/%s/%s/%s?apiKey=%s' % (market, currency, language, origin, destination, departure_date, returning_date, token) 


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


def filter_quotes(budget, quotes, min_percentage=50, max_percentage=110):
    min_price = int(float(budget) * min_percentage / 100)
    max_price = int(float(budget) * max_percentage / 100)

    quotes = filter(lambda q: min_price <= q.get('MinPrice') <= max_price, quotes)
    quotes = sorted(quotes, key=lambda q: q.get('MinPrice'))

    return quotes


async def browse_quotes(origin, destination, departure_date, returning_date, token, market='ID', currency='IDR', language='en-US'):
    url = 'http://partners.api.skyscanner.net/apiservices/browsequotes/v1.0/%s/%s/%s/%s/%s/%s/%s?apiKey=%s' % (market, currency, language, origin, destination, departure_date, returning_date, token)
    print('Quotes URL: %s' % url)
    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    return response.json()


async def browse_quotes_by_dates(origin, destination, departure_date, returning_date, token, market='ID', currency='IDR', language='en-US'):
    print(destination)
    url = 'http://partners.api.skyscanner.net/apiservices/browsedates/v1.0/%s/%s/%s/%s/%s/%s/%s?apiKey=%s' % (market, currency, language, origin, destination, departure_date, returning_date, token)
    print('Quotes URL: %s' % url)
    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    return response.json()


def get_origin(origin, ip_address, force_origin_from_skyscanner_place_id=False):
    # if isinstance(origin, dict):
    #     lat = origin.get('lat')
    #     lon = origin.get('lon')

    #     if lat and lon:
    #         return '%s,%s-Latlong' % (lat, lon)

    if force_origin_from_skyscanner_place_id:
        return origin

    if ip_address == '127.0.0.1-ip' or ip_address == 'None-ip':
        ip_address = '66.96.251.154-ip'

    print('IP Address: %s' % ip_address)

    return ip_address


def format_browse_by_dates_quotes(row):
    return {
        'price': row.get('Price'),
        'date': row.get('PartialDate'),
        'quote_datetime': row.get('QuoteDateTime')
    }


async def search_by_dates(token, origin, destination, departure_date, returning_date, market='ID', currency='IDR', language='en-US'):
    json = await browse_quotes_by_dates(origin, destination, departure_date, returning_date, token, market, currency, language)

    inbounds = json.get('Dates').get('InboundDates')
    outbounds = json.get('Dates').get('OutboundDates')

    if not inbounds or not outbounds:
        return {}

    return {
        'outbound_dates': [format_browse_by_dates_quotes(outbound) for outbound in outbounds],
        'inbound_dates': [format_browse_by_dates_quotes(inbound) for inbound in inbounds],
    }


async def search_flights(token, origin, ip_address, destination, departure_date, returning_date, budget, market='ID', currency='IDR', language='en-US'):
    force_origin_from_skyscanner_place_id = True if isinstance(origin, str) and origin.endswith('-sky') else False
    print('Force origin %s: %s' % (origin, force_origin_from_skyscanner_place_id))
    origin = get_origin(origin=origin,
                        ip_address=ip_address,
                        force_origin_from_skyscanner_place_id=force_origin_from_skyscanner_place_id)

    json = await browse_quotes(origin, destination, departure_date, returning_date, token, market, currency, language)
    quotes = json.get('Quotes')

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

    # Filter
    quotes = filter_quotes(budget=budget, 
                           quotes=quotes,
                           min_percentage=40,
                           max_percentage=110)
    
    return destinations