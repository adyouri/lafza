from flask_restplus import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError
from project.models import User, db
from flask import request

api = Namespace('users')

register_model = api.model('Register', {
                       'username': fields.String(required=True),
                       'password': fields.String(required=True),
                       'email': fields.String,
                       })


@api.route('/register/', endpoint='register')
class RegisterAPI(Resource):
    @api.expect(register_model)
    def post(self):
        api_payload = request.get_json()
        username = api_payload['username']
        password = api_payload['password']
        email = api_payload['email']
        new_user = User(username=username,
                        # guard.encrypt_password(password)
                        password_hash=password,
                        email=email)

        # Try adding user
        try:
            db.session.add(new_user)
            db.session.commit()

        # Username already exists in the database
        except IntegrityError:
            db.session.rollback()
            return {'Error': '{} already exists'.format(new_user.username),
                    'URL': api.url_for('user',
                                       username=new_user.username)}, 400

        # User was added
        return {'created:': new_user}, 201
