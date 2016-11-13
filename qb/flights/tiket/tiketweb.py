from bs4 import BeautifulSoup
from qb.flights.skyscanner.skyscanner import get_referral_link
import requests


def process_destination(origin, destination, departure_date, returning_date, outbound_airline, inbound_airline, price, skyscanner_token):
    return {
        'outbound': {
            'quote_id': 'not_from_skyscanner',
            'airline': outbound_airline
        },
        'inbound': {
            'quote_id': 'not_from_skyscanner',
            'airline': inbound_airline
        },
        'airports': {
            'origin': {
                'city_id': origin,
                'city_name': origin,
                'iata_code': origin,
                'country_name': 'not_from_skyscanner',
                'airport_name': origin
            },
            'destination': {
                'city_id': destination,
                'city_name': destination,
                'iata_code': destination,
                'country_name': 'not_from_skyscanner',
                'airport_name': destination
            }
        },
        'dates': {
            'outbound': departure_date,
            'inbound': returning_date
        },
        'referral_link': get_referral_link(skyscanner_token, 
                                           origin, 
                                           destination, 
                                           departure_date, 
                                           returning_date),
        'cheapest': int(price)
    }


async def search_flights(origin, destination, departure_date, returning_date, skyscanner_token, adults=1, children=0, infants=0):
    url = 'http://www.tiket.com/pesawat/cari?d=%s&a=%s&date=%s&ret_date=%s&adult=%s&child=%s&infant=%s'
    url = url % (origin, destination, departure_date, returning_date, adults, children, infants)

    headers = {
        'Referer': 'http://www.tiket.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'Connection': 'keep-alive',
        'Accept-Language': 'en-US,en;q=0.8,id;q=0.6',
        'Cookie': "device[type]=x; userlang=id; TIKETSESSID=h1f89cp656j60klv9dl8q10rhkjmh9ee; PHPSESSID=ws2pow_sl~lpa3tdjm8e4tvg65mq3diouqjkee74mc; usercurrency=IDR"
    }

    response = requests.get(url, headers=headers)

    body = response.text
    if not 'summary_pricetotal' in body:
        return None

    tree = BeautifulSoup(body, 'lxml')

    price = tree.find(id='summary_pricetotal').get('rel')
    if not price or int(price) == 0:
        return None

    print('%s - IDR %s' % (destination, price))
    try:
        outbound_airline = tree.find(id='summary_depart').find('td', {'class': 't3'}).small.string.split()
        outbound_airline = ' '.join(outbound_airline)
        inbound_airline = tree.find(id='summary_return').find('td', {'class': 't3'}).small.string.split()
        inbound_airline = ' '.join(inbound_airline)
    except AttributeError:
        return None

    return process_destination(origin, destination, departure_date, returning_date, outbound_airline, inbound_airline, price, skyscanner_token)
