import json

from flask import url_for
import pytest


@pytest.mark.usefixtures('client_class')
class TestUsers:
    def test_register(self):
        new_user_data = json.dumps(
                                   dict(username='tester',
                                        password='secret',
                                        email='tester@example.com'
                                        )
                                   )

        res = self.client.post(url_for('main_api.register'),
                               content_type='application/json',
                               data=new_user_data
                               )

        assert res.status_code == 201
        assert b'user admin successfully registred'

    def test_login(self):
        self.test_register()
        user_data = json.dumps(
                               dict(username='tester',
                                    password='secret'
                                    )
                               )

        res = self.client.post(url_for('main_api.login'),
                               content_type='application/json',
                               data=user_data
                               )

        assert res.status_code == 200
        assert 'access_token' in res.json.keys()

    def test_failed_login(self):
        user_data = json.dumps(
                               dict(username='no_username',
                                    password='s3cret'
                                    )
                               )
        res = self.client.post(url_for('main_api.login'),
                               content_type='application/json',
                               data=user_data
                               )
        assert res.status_code == 401
        assert res.json['Error'] == 'Wrong credintials'
