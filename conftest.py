from datetime import datetime

import pytest

from project import create_app
from project.models import db, Term, Translation, User


@pytest.fixture
def app():
    app = create_app('../testing_config.cfg')
    # Push the application context for the db object to work properly
    app.app_context().push()
    # Rollback all previous session changes from the last test run
    db.session.rollback()
    # Delete all the tables
    db.drop_all()

    # Create all tables
    db.create_all()
    # Add a new term
    term = Term(term='term')
    # Add a new translation
    translation = Translation(translation='translation')
    # Make the dates constant
    test_date_created = datetime(2018, 1, 1)
    test_modified_date = datetime(2018, 1, 2)
    translation.date_created = test_date_created
    translation.modified_date = test_modified_date
    term.date_created = test_date_created
    # Add the translation to term translations
    term.translations.append(translation)
    # Create a new user
    user = User(username='test', password='secret', email='usr@example.com')
    # Add term and user, this also adds the translation to the session
    db.session.add(term)
    db.session.add(user)
    db.session.commit()

    # Yield the app object
    yield app

    # DB Teardown
    db.session.rollback()
    db.drop_all()
