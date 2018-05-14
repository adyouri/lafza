from flask_praetorian import Praetorian
guard = Praetorian()

# A set for storing blacklisted JWT tokens (This should use Redis instead)
jwt_blacklist = set()


def is_blacklisted(jti):
    """
    check whether a JWT token is blacklisted or not.

    This is Flask-Praetorian specific (see guard.init_app() below).

    :param jti: The token's JTI (which is unique for each token)
    """
    return jti in jwt_blacklist
