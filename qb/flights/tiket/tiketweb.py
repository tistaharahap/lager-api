from bs4 import BeautifulSoup
from qb.flights.skyscanner.skyscanner import get_referral_link
import redis
import requests
import json


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
            'origin': origin,
            'destination': destination
        },
        'dates': {
            'outbound': departure_date,
            'inbound': returning_date
        },
        'referral_link': get_referral_link(skyscanner_token, 
                                           origin.get('iata_code'), 
                                           destination.get('iata_code'), 
                                           departure_date, 
                                           returning_date),
        'cheapest': int(price)
    }


def build_redis_key(origin, destination, departure_date, returning_date, adults, children, infants):
    return '%s#%s#%s#%s#%s#%s#%s' % (origin, destination, departure_date, returning_date, adults, children, infants)


async def search_flights(origin, destination, departure_date, returning_date, skyscanner_token, budget, adults=1, children=0, infants=0):
    redis_conn = redis.StrictRedis(host='127.0.0.1',
                                   port=6379,
                                   db=7)
    redis_key = build_redis_key(origin.get('iata_code'), destination.get('iata_code'), departure_date, returning_date, adults, children, infants)
    result = redis_conn.get(redis_key)
    if result:
        return json.loads(str(result, 'utf-8'))

    url = 'http://www.tiket.com/pesawat/cari?d=%s&a=%s&date=%s&ret_date=%s&adult=%s&child=%s&infant=%s'
    url = url % (origin.get('iata_code'), destination.get('iata_code'), departure_date, returning_date, adults, children, infants)
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
        print('No price found')
        return None

    try:
        outbound_airline = tree.find(id='summary_depart').find('td', {'class': 't3'}).small.string.split()
        outbound_airline = ' '.join(outbound_airline)
        inbound_airline = tree.find(id='summary_return').find('td', {'class': 't3'}).small.string.split()
        inbound_airline = ' '.join(inbound_airline)
    except AttributeError:
        print('No airline info found')
        return None

    print('%s - IDR %s' % (destination.get('iata_code'), price))

    result = process_destination(origin, destination, departure_date, returning_date, outbound_airline, inbound_airline, price, skyscanner_token)
    redis_conn.setex(redis_key, 60*60*24, json.dumps(result))

    return result
