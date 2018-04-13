from flask_restplus import Namespace, Resource, fields
from flask import request
from flask_praetorian import Praetorian, auth_required, current_user
from flask_praetorian.exceptions import MissingUserError

from project.models import db
from project.schemas import UserSchema

import project.core.user_utils as user_utils

guard = Praetorian()

api = Namespace('users')

user_schema = UserSchema()

# Flask-Restplus models
login_model = api.model('Login', {
                        'username': fields.String(required=True,
                                                  min_length=3,
                                                  max_length=25),

                        'password': fields.String(required=True,
                                                  min_length=8),
                        })

register_model = api.inherit('Register', login_model, {
                           'email': fields.String(pattern='\S+@\S+\.\S+',
                                                  example='email@example.com')
                           })


@api.route('/register/', endpoint='register')
class RegisterAPI(Resource):
    @api.expect(register_model)
    def post(self):
        api_payload = request.get_json()
        password = api_payload['password']
        username = api_payload['username']
        email = api_payload['email']

        # Password encryption should probably be done in pre_load
        api_payload['password'] = guard.encrypt_password(password)

        user_is_not_unique = None
        if not user_utils.user_is_unique(username=username,
                                         email=email):
            user_is_not_unique = True

        new_user = user_schema.load(api_payload)

        # Check username and email are unique
        if user_is_not_unique:
            message = ['Username or email already exist']
            new_user.errors['username'] = message
            new_user.errors['email'] = message

        if new_user.errors:
            return dict(errors=new_user.errors), 400

        # Add user
        db.session.add(new_user.data)
        db.session.commit()
        result = user_schema.dump(new_user)
        return result.data, 201


@api.route('/login', endpoint='login')
class LoginAPI(Resource):

    @api.expect(login_model)
    def post(self):
        api_payload = request.get_json()
        username = api_payload['username']
        password = api_payload['password']
        try:
            user = guard.authenticate(username, password)
            access_token = {'access_token': guard.encode_jwt_token(user)}
            return access_token, 200
        except MissingUserError:
            return {'Error': 'Wrong credintials'}, 401


@api.route('/protected')
class protectedAPI(Resource):
    ''' Experimental API '''
    decorators = [auth_required]

    def get(self):
        return {'message': 'Welcome {}'.format(current_user().username)}, 200
