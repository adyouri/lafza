from flask import Flask
from flask_migrate import Migrate

# A set for storing blacklisted JWT tokens (This should use Redis instead)
jwt_blacklist = set()


def is_blacklisted(jti):
    """
    check whether a JWT token is blacklisted or not.

    This is Flask-Praetorian specific (see guard.init_app() below).

    :param jti: The token's JTI (which is unique for each token)
    """
    return jti in jwt_blacklist


def create_app(config_file):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)

    # Database
    from project.models import db
    db.init_app(app)
    migrate = Migrate(app, db)

    # flask-praetorian
    from project.api.v1.users import guard
    from project.models import User
    guard.init_app(app, User, is_blacklisted=is_blacklisted)

    # flask-marshmallow
    from project.schemas import ma
    ma.init_app(app)

    # Blueprints
    from project.views.main import main
    from project.api.v1.main import main_api
    app.register_blueprint(main)
    app.register_blueprint(main_api, url_prefix='/api/v1')

    return app
