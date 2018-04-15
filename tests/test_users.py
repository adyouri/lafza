import json

from flask import url_for
import pytest

from project.schemas import USERNAME_ERROR, PASSWORD_ERROR


def register(username, password, email, client):
        new_user_data = json.dumps(
                                   dict(username=username,
                                        password=password,
                                        email=email
                                        )
                                   )

        return client.post(url_for('main_api.register'),
                           content_type='application/json',
                           data=new_user_data
                           )


def login(username, password, client):
    user_data = json.dumps(
                            dict(username=username,
                                 password=password
                                 )
                            )

    return client.post(url_for('main_api.login'),
                       content_type='application/json',
                       data=user_data
                       )


@pytest.mark.usefixtures('client_class')
class TestUsers:
    def test_register(self):
        res = register('tester',
                       '12345secret',
                       'tester@example.com',
                       client=self.client)

        assert res.status_code == 201
        assert b'user admin successfully registred'

    def test_login(self):
        register('tester',
                 '12345secret',
                 'tester@example.com',
                 client=self.client)
        res = login('tester', '12345secret', client=self.client)
        assert res.status_code == 200
        assert 'access_token' in res.json.keys()

    def test_failed_login(self):
        res = login('no_username', '12345secret', client=self.client)
        assert res.status_code == 401
        assert res.json['Error'] == 'Wrong credintials'

    def test_username_is_too_short(self):
        res = login('aa', '12345secret', client=self.client)
        assert res.status_code == 400
        assert res.json['errors']['username'] == USERNAME_ERROR

    def test_password_is_too_short(self):
        res = login('username', '123', client=self.client)
        assert res.status_code == 400
        assert res.json['errors']['password'] == PASSWORD_ERROR

    def test_failed_register(self):
        res = register('aa', '123', 'invalid email', client=self.client)
        assert res.status_code == 400
        assert USERNAME_ERROR in res.json['errors']['username']
        assert PASSWORD_ERROR in res.json['errors']['password']
        email_error = "Not a valid email address."
        assert email_error in res.json['errors']['email']
