# Library imports
from flask_restplus import Namespace, Resource, fields
from flask import request
from flask_praetorian import auth_required, current_user
from flask_praetorian.exceptions import MissingUserError

# Local imports
from project.models import db
import project.core.user_utils as user_utils
from project.auth import guard, jwt_blacklist
from project.schemas import UserSchema

api = Namespace('users')


user_schema = UserSchema(
        dump_only=('date_created',
                   'translations',
                   'terms',
                   'roles')
        )

# Flask-Restplus models for documentation
login_model = api.model('Login', {
                        'username': fields.String(required=True,
                                                  min_length=3,
                                                  max_length=25),

                        'password': fields.String(required=True,
                                                  min_length=8),
                        })

register_model = api.inherit('Register', login_model, {
                           'email': fields.String(example='email@example.com')
                           })


@api.route('/register/', endpoint='register')
class RegisterAPI(Resource):
    @api.expect(register_model)
    def post(self):
        ''' Register a new user '''
        api_payload = request.get_json()
        username = api_payload['username']
        email = api_payload['email']
        user_is_not_unique = None
        # Check if username and email are unique values
        if not user_utils.user_is_unique(username=username,
                                         email=email):
            user_is_not_unique = True

        # Load the API payload
        new_user = user_schema.load(api_payload)

        # If username or email is not unique, declare the error
        if user_is_not_unique:
            message = ['Username or email already exist']
            new_user.errors['username'] = message
            new_user.errors['email'] = message

        if new_user.errors:
            # Return validation errors if they exist
            return dict(errors=new_user.errors), 400

        # Add the user to the database
        db.session.add(new_user.data)
        db.session.commit()
        # Dump the new user data and return it
        result = user_schema.dump(new_user.data)
        return result.data, 201


@api.route('/login', endpoint='login')
class LoginAPI(Resource):
    @api.expect(login_model)
    def post(self):
        ''' User login route '''
        api_payload = request.get_json()
        # Get the username and password
        username = api_payload['username']
        password = api_payload['password']
        try:
            # Try to authenticate the user
            user = guard.authenticate(username, password)
            # Generate the JWT access token
            access_token = {'access_token': guard.encode_jwt_token(user)}
            return access_token, 200
        except MissingUserError:
            return {'error': 'Wrong credentials.'}, 401


@api.route('/protected', endpoint='protected')
class protectedAPI(Resource):
    ''' Experimental API '''
    method_decorators = [auth_required]

    def get(self):
        return {'message': 'Welcome {}'.format(current_user().username)}, 200


@api.route('/refresh', endpoint='refresh')
class refreshAPI(Resource):
    ''' Refresh an expired JWT token '''
    def get(self):
        old_token = guard.read_token_from_header()
        new_token = guard.refresh_jwt_token(old_token)
        return {'access_token': new_token}, 200


@api.route('/logout', endpoint='logout')
class logoutAPI(Resource):
    '''Logout an authenticated user by blacklisting their token'''
    method_decorators = [auth_required]

    def get(self):
        jwt_token = guard.read_token_from_header()
        # Extract JWT data from the token
        data = guard.extract_jwt_token(jwt_token)
        # Add the token's jti to the blacklist
        jwt_blacklist.add(data['jti'])
        return {'message': 'Successfully logged out'}, 200
