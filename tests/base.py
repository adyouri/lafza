import json
from flask import url_for


def make_json_request(http_method, endpoint, headers={}, data=None):
    """
    Return a response object from a Flask test client http method.

    :param http_method: HTTP method to be used for the request (ie. client.get)
    :param endpoint: Request Endpoint (ie. 'main_api.terms')
    :param headers: HTTP headers
    :param data: Data to be sent if it's a POST/PATCH request

    :returns: Response object

    Usage::

        >>> test_client = app.test_client()
        >>> with app.test_request_context(): # request context for url_for()
        ...     res = make_json_request(http_method=test_client.get,
        ...                             endpoint='main_api.terms')
        ...
        >>> res.status_code # UNAUTHORIZED, because we haven't authenticated
        401
    """
    response = http_method(
                           url_for(endpoint),
                           content_type='application/json',
                           data=data,
                           headers=headers,
                           )
    return response


def length_error(_min, _max):
    """
    Return a Marshmallow length error according to the min and max values.

    :param _min: the minimum length.
    :param _max: the maximum length.
    """
    return f'Length must be between {_min} and {_max}.'


def valid_jwt_token(client):
    """
    Return a valid JWT token to use with routes that require authentication.

    :param client: test client for sending a POST request to /api/v1/login.
    :returns: A JWT token.
    """
    # User JSON data
    # The user was added to the database in conftest.py

    user_data = json.dumps(
            dict(
                username='test',
                password='secret',
                )
            )

    # Login
    response = client.post(
                url_for('main_api.login'),
                content_type='application/json',
                data=user_data
                )

    # Extract the token from the response and format the header
    token = response.json['access_token']
    header = f'Bearer {token}'

    return header
