from flask import Flask
from flask_migrate import Migrate


def create_app(config_file):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)

    from project.models import db
    db.init_app(app)
    migrate = Migrate(app, db)

    from project.views.main import main
    from project.api.v1.main import main_api
    app.register_blueprint(main)
    app.register_blueprint(main_api, url_prefix='/api/v1')

    return app
