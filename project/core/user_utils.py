from project.models import User


def user_is_unique(username, email):
    '''Validate that username and email are unique'''
    username = User.query.filter_by(username=username).first()
    email = User.query.filter_by(email=email).first()
    if username or email:
        return False
    return True
