import requests


async def find_carrier(carrier_id, carriers):
    for carrier in carriers:
        if carrier.get('CarrierId') == carrier_id:
            return carrier


async def find_destination(dest_id, places):
    for place in places:
        if int(place.get('PlaceId')) == int(dest_id):
            return place


def get_referral_link(token, origin, destination, departure_date, returning_date):
    '''
    http://partners.api.skyscanner.net/apiservices/referral/v1.0/GB/GBP/en-GB/EDI/CDG/2014-12-12/2014-12-20?apiKey=prtl674938798674
    '''

    return 'http://partners.api.skyscanner.net/apiservices/referral/v1.0/ID/IDR/en-US/%s/%s/%s/%s?apiKey=%s' % (origin.get('iata_code'), destination, departure_date, returning_date, token) 


async def search_flights(token, origin, destination, departure_date, returning_date, budget):
    url = 'http://partners.api.skyscanner.net/apiservices/browsequotes/v1.0/ID/IDR/en-US/%s/%s/%s/%s?apiKey=%s' % (origin.get('iata_code'), destination, departure_date, returning_date, token)

    headers = {
        'Accept': 'application/json'
    }

    request = requests.get(url, headers=headers)
    json = request.json()
    if not json:
        return []

    quotes = json.get('Quotes')
    quotes = sorted(quotes, key=lambda e: e.get('MinPrice'))

    min_price = int(float(budget) * 0.5)
    max_price = int(float(budget) * 1.5)

    quotes = filter(lambda q: min_price <= q.get('MinPrice') <= max_price, quotes)
    json['Quotes'] = quotes

    carriers = json.get('Carriers')
    places = json.get('Places')

    destinations = []

    for quote in quotes:
        outbound_leg = quote.get('OutboundLeg')
        if not outbound_leg:
            continue

        inbound_leg = quote.get('InboundLeg')
        if not inbound_leg:
            continue

        outbound_carrier_ids = outbound_leg.get('CarrierIds')
        if not outbound_carrier_ids:
            continue

        inbound_carrier_ids = inbound_leg.get('CarrierIds')
        if not inbound_carrier_ids:
            continue

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
            'referral_link': get_referral_link(token, origin, destination_airport.get('IataCode'), departure_date, returning_date),
            'cheapest': quote.get('MinPrice')
        }

        destinations.append(destination)
    
    return destinations