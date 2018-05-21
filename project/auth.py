from datetime import timedelta
import redis
from flask import current_app
from flask_praetorian import Praetorian

guard = Praetorian()


class BlackList:
    """
    This class is supposed to behave like a Python set.

    So that Redis can be easily replaced with a regular Python set.

    Usage::
        >>> jwt_blacklist = BlackList()
        >>> jwt_blacklist.add('value')
        >>> 'value' in jwt_blacklist
        True
        >>> 'another_value' in jwt_blacklist
        False
    """
    _redis_blacklist = redis.StrictRedis(host='localhost',
                                         port=6379,
                                         db=0,
                                         decode_responses=True,
                                         )

    def add(self, jti):
        """
        Add a jti to the Redis blacklist

        Will also set it to automatically expire after the token expires

        :param jti: The token's JTI (which is unique for each token)
        """
        expire_time = timedelta(**current_app.config['JWT_REFRESH_LIFESPAN'])
        self._redis_blacklist.set(jti,
                                  'blacklisted',
                                  expire_time,
                                  )

    def __contains__(self, key):
        """
        Override the behavior of the in operator.

        Example::
            >>> item in items # this calls items.__contains__(item)
        """
        result = self._redis_blacklist.get(key)
        return bool(result)  # True if the key exists, False if result is None


jwt_blacklist = BlackList()


def is_blacklisted(jti):
    """
    Check whether a JWT token is blacklisted or not.

    Used by Flask-Praetorian to check whether a JWT token is still valid or not

    :param jti: The token's JTI (which is unique for each token)
    """
    return jti in jwt_blacklist
