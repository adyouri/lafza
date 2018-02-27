from datetime import datetime

from project import create_app
import pytest
from project.models import db, Term, Translation


@pytest.fixture
def app():
    app = create_app('../testing_config.cfg')
    app.app_context().push()
    # DB Setup
    db.create_all()
    term = Term(term='term')
    translation = Translation(translation='translation')
    test_created_date = datetime(2018, 1, 1)
    test_modified_date = datetime(2018, 1, 2)
    translation.created_date = test_created_date
    translation.modified_date = test_modified_date
    term.created_date = test_created_date
    term.translations.append(translation)
    db.session.add(term)
    db.session.commit()

    yield app

    # DB Teardown
    db.drop_all()
