import json
from flask import url_for


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
