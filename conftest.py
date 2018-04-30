from datetime import datetime
import json

from flask import url_for

from project import create_app
import pytest
from project.models import db, Term, Translation, User


@pytest.fixture
def app():
    app = create_app('../testing_config.cfg')
    app.app_context().push()
    # DB Setup
    db.session.rollback()
    db.drop_all()

    db.create_all()
    term = Term(term='term')
    translation = Translation(translation='translation')
    test_date_created = datetime(2018, 1, 1)
    test_modified_date = datetime(2018, 1, 2)
    translation.date_created = test_date_created
    translation.modified_date = test_modified_date
    term.date_created = test_date_created
    term.translations.append(translation)

    user = User(username='admin', password='12345678', email='usr@example.com')
    db.session.add(term)
    db.session.add(user)
    db.session.commit()

    yield app

    # DB Teardown
    db.session.rollback()
    db.drop_all()


@pytest.fixture
def authenticated_client(app):
    """Return a test client with an authenticated user."""
    user_data = json.dumps(
                            dict(username='admin',
                                 password='12345678',
                                 )
                            )
    client = app.test_client()
    res = client.post(
            url_for('main_api.login'),
            content_type='application/json',
            data=user_data,
            )
    token = res.json['token']
    import pdb; pdb.set_trace()
    return client

def test_auth(app):
    authenticated_client(app)
