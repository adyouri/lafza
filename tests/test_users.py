import json
import time

from flask import url_for, current_app
import pytest

from project import auth
import base

EMAIL_ERROR = 'Not a valid email address.'
PASSWORD_LENGTH_ERROR = base.length_error(8, 50)
USERNAME_LENGTH_ERROR = base.length_error(3, 25)
EMAIL_LENGTH_ERROR = base.length_error(6, 50)


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
    def jwt_header(self):
        jwt = base.valid_jwt_token(client=self.client)
        return jwt

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
        assert res.json['error'] == 'Wrong credentials.'

    def test_login_wrong_username(self):
        register('tester',
                 '12345secret',
                 'tester@example.com',
                 client=self.client)
        res = login('tester__', '12345secret', client=self.client)
        assert res.status_code == 401
        assert res.json['error'] == 'Wrong credentials.'

    def test_login_wrong_password(self):
        register('tester',
                 '12345secret',
                 'tester@example.com',
                 client=self.client)
        res = login('tester', '12345secret__', client=self.client)
        assert res.status_code == 401
        assert res.json['error'] == 'Wrong credentials.'

    def test_failed_register(self):
        res = register('aa', '123', 'invalid email', client=self.client)
        assert res.status_code == 400
        assert USERNAME_LENGTH_ERROR in res.json['errors']['username']
        assert PASSWORD_LENGTH_ERROR in res.json['errors']['password']
        assert EMAIL_ERROR in res.json['errors']['email']

    # Test user registration using parametrization
    @pytest.mark.parametrize(
        'username, email, password, status_code, message',
        [
         ('us', 'user@example.com', '12345678', 400, USERNAME_LENGTH_ERROR),
         ('us'*50, 'user@example.com', '12345678', 400, USERNAME_LENGTH_ERROR),
         ('us', 'user@example.com', '123', 400, PASSWORD_LENGTH_ERROR),
         ('us', 'user@example.com', '123'*100, 400, PASSWORD_LENGTH_ERROR),
         ('user', 'user example.com', '12345678', 400, EMAIL_ERROR),
         ('user', f"{'u'*55}@u.c", '12345678', 400, EMAIL_LENGTH_ERROR),
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

    def test_refresh_jwt_token(self):
        jwt_header = self.jwt_header()
        time.sleep(1.5)
        res = self.client.get(url_for('main_api.protected'),
                              content_type='application/json',
                              headers={'Authorization': jwt_header}
                              )
        assert res.status_code == 401
        res = self.client.get(url_for('main_api.refresh'),
                              content_type='application/json',
                              headers={'Authorization': jwt_header}
                              )
        new_token = res.json['access_token']
        res = self.client.get(url_for('main_api.protected'),
                              content_type='application/json',
                              headers={'Authorization': f'Bearer {new_token}'}
                              )
        assert res.status_code == 200

    def test_logout(self):
        jwt_header = self.jwt_header()
        current_app.config['JWT_REFRESH_LIFESPAN'] = {'seconds': 1}

        _, _, jwt_token = jwt_header.partition('Bearer ')
        jti = auth.guard.extract_jwt_token(jwt_token)['jti']

        # Access a protected route
        res = self.client.get(url_for('main_api.protected'),
                              content_type='application/json',
                              headers={'Authorization': jwt_header}
                              )
        assert res.status_code == 200

        # Logout
        res = self.client.get(url_for('main_api.logout'),
                              content_type='application/json',
                              headers={'Authorization': jwt_header}
                              )
        assert res.status_code == 200

        # Check that the jwt token's jti is in the blacklist
        assert jti in auth.jwt_blacklist
        # import pdb; pdb.set_trace()

        # Try accessing the route again
        res = self.client.get(url_for('main_api.protected'),
                              content_type='application/json',
                              headers={'Authorization': jwt_header}
                              )

        assert res.status_code == 403

        # wait for the refresh token to expire
        # and check that jwt is no longer in the blacklist
        time.sleep(1)
        assert jti not in auth.jwt_blacklist


    def test_jwt_access_token_expiration(self):
        jwt_header = self.jwt_header()
        time.sleep(1.5)
        res = self.client.get(url_for('main_api.protected'),
                              content_type='application/json',
                              headers={'Authorization': jwt_header}
                              )
        assert res.status_code == 401
        assert res.json['error'] == 'ExpiredAccessError'

    def test_jwt_refresh_token_expiration(self):
        jwt_header = self.jwt_header()
        time.sleep(2.5)
        res = self.client.get(url_for('main_api.refresh'),
                              content_type='application/json',
                              headers={'Authorization': jwt_header}
                              )
        assert res.status_code == 401
        assert res.json['error'] == 'ExpiredRefreshError'
