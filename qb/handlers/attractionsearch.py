import requests


def resolve_photo(photo):
    return {
        'url': 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=1200&photoreference=%s&key=AIzaSyDgAOfmll7dUGJ3Et_NJN1MtUMJPitDD8c' % photo.get('photo_reference'),
        'attribution': photo.get('html_attributions')
    }

async def handle_attraction_search(request):
    meta = request.json.get('meta')
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s,%s&radius=10000&keyword=attractions&type=point_of_interest&key=AIzaSyDgAOfmll7dUGJ3Et_NJN1MtUMJPitDD8c' % (meta.get('lat'), meta.get('lon'))

    response = requests.get(url)
    json = response.json()

    results = json.get('results')

    places = []
    for result in results:
        photos = result.get('photos')
        if not photos:
            continue

        places.append({
            'location': result.get('geometry').get('location'),
            'name': result.get('name'),
            'photos': [resolve_photo(photo) for photo in photos] if photos else [],
            'rating': result.get('rating'),
            'vicinity': result.get('vicinity')
        })

    return dict(data=places)