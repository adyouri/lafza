import json

from flask import url_for
import pytest

from project.schemas import USERNAME_ERROR, PASSWORD_ERROR
EMAIL_ERROR = 'Not a valid email address.'


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
        assert res.json['error'] == 'Wrong credintials'

    def test_login_wrong_username(self):
        register('tester',
                 '12345secret',
                 'tester@example.com',
                 client=self.client)
        res = login('tester__', '12345secret', client=self.client)
        assert res.status_code == 401
        assert res.json['error'] == 'Wrong credintials'

    def test_login_wrong_password(self):
        register('tester',
                 '12345secret',
                 'tester@example.com',
                 client=self.client)
        res = login('tester', '12345secret__', client=self.client)
        assert res.status_code == 401
        assert res.json['error'] == 'Wrong credintials'

    def test_failed_register(self):
        res = register('aa', '123', 'invalid email', client=self.client)
        assert res.status_code == 400
        assert USERNAME_ERROR in res.json['errors']['username']
        assert PASSWORD_ERROR in res.json['errors']['password']
        email_error = EMAIL_ERROR
        assert email_error in res.json['errors']['email']

    # Test user registration using parametrization
    @pytest.mark.parametrize(
        'username, email, password, status_code, message',
        [('us', 'user@example.com', '12345678', 400, USERNAME_ERROR),
         ('us', 'user@example.com', '123', 400, PASSWORD_ERROR),
         ('user', 'user example.com', '12345678', 400, EMAIL_ERROR),
         ('test_user1', 'user@example.com', '012345678', 201, 'test_user1'),
         ]
        )
    def test_parametrized_register(self,
                                   username,
                                   email,
                                   password,
                                   status_code,
                                   message):
        '''Test adding a new user'''
        new_user_data = json.dumps(dict(
                                      username=username,
                                      email=email,
                                      password=password,
                                      roles='admin',
                                      date_created='2018-01-11T15:43:00'
                                      ))

        res = self.client.post(url_for('main_api.register'),
                               content_type='application/json',
                               data=new_user_data
                               )
        assert res.status_code == status_code
        assert message.encode(encoding='UTF-8') in res.data
        if res.status_code == 201:
            assert res.json['date_created'] != '2018-01-11T15:43:00+00:00'
            assert res.json['roles'] != 'admin'
