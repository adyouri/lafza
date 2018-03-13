from flask_restplus import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError
from flask import request
from flask_praetorian import Praetorian, auth_required, current_user
from flask_praetorian.exceptions import MissingUserError

from project.models import User, db

guard = Praetorian()

api = Namespace('users')

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
    @api.expect(register_model, validate=True)
    def post(self):
        api_payload = request.get_json()
        username = api_payload['username']
        password = api_payload['password']
        email = api_payload['email']
        new_user = User(username=username,
                        password=guard.encrypt_password(password),
                        email=email)

        # Try adding user
        try:
            db.session.add(new_user)
            db.session.commit()

        # Username or email already exists in the database
        except IntegrityError:
            db.session.rollback()
            return {'Error': 'Username or email already exists'}, 400

        # User was added
        user = new_user.username
        message = {'message': 'User {} successfully registred'.format(user)}
        return message, 201


@api.route('/login', endpoint='login')
class LoginAPI(Resource):

    @api.expect(login_model, validate=True)
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