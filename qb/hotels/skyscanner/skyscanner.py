import requests


async def create_session(token, checkin_date, checkout_date, location, guests=1, rooms=1, market='ID', currency='IDR', locale='en-US'):
	headers = {
		'Accept': 'application/json'
	}
	entity_id = '%s,%s-latlong' % (location.get('lat'), location.get('lon'))
	url = 'http://partners.api.skyscanner.net/apiservices/hotels/liveprices/v2/%s/%s/%s/%s/%s/%s/%s/%s?apiKey=%s' % (market, currency, locale, entity_id, checkin_date, checkout_date, guests, rooms, token)
	print(url)
	response = requests.get(url, headers=headers)
	print(response.text)

	return response.headers


async def search_hotels(token, checkin_date, checkout_date, location, guests=1, rooms=1, market='ID', currency='IDR', locale='en-US'):
	url = await create_session(token, checkin_date, checkout_date, location, guests, rooms, market, currency, locale)

	print(url)

	return []