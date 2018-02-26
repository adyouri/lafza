from project import create_app
import pytest

@pytest.fixture
def app():
    app = create_app('../testing_config.cfg')
    return app
