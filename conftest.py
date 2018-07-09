from datetime import datetime

import pytest

from project import create_app
from project.models import db, Term, Translation, User
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


@pytest.fixture
def app():
    app = create_app('../testing_config.cfg')
    # Push the application context for the db object to work properly
    app.app_context().push()
    # Rollback all previous session changes from the last ran tests
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

    # Create an author
    author = User(username='author',
                  password='secret',
                  email='author@example.com')
    # Create an admin user
    admin = User(username='admin',
                 password='secret',
                 roles='admin,user',
                 email='admin@example.com')

    # Create a term and assign it to "author"
    author_term = Term(term='author_term')
    author_term.author = author

    # Add terms and users, this also adds the translation to the session
    db.session.add(term)
    db.session.add(user)
    db.session.add(admin)
    db.session.add(author_term)

    # Create a translation and assign it to "author"
    author_translation = Translation(translation='author_translation')
    author_translation.author = author
    author_translation.term = author_term
    db.session.add(author_translation)

    db.session.commit()

    # All the code after the yield statement serves as the teardown code
    yield app

    # DB Teardown
    db.session.rollback()
    db.drop_all()
