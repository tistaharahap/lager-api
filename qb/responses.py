from sanic.response import json


def init_responses(app):
    @app.middleware('response')
    def format_response(request, response):
        status = response.get('status')
        status = status if status else 200
        
        message = response.get('message')
        message = message if message else ''

        headers = response.get('headers')

        data = response.get('data')

        response = {
            'status': status,
            'message': message,
            'data': data
        }

        return json(response, 
                    status=status,
                    headers=headers)