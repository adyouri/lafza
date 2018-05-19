from datetime import timedelta
import redis
from flask import current_app
from flask_praetorian import Praetorian
guard = Praetorian()

# A set for storing blacklisted JWT tokens (This should use Redis instead)
# jwt_blacklist = set()


class BlackList:
    """ This class is supposed to behave like a Python set """
    _redis_blacklist = redis.StrictRedis(host='localhost',
                                         port=6379,
                                         db=0,
                                         decode_responses=True,
                                         )

    def add(self, jti):
        """
        Add a jti to the redis blacklist

        Will also set it to automatically expire after the token expires
        :param jti: The token's JTI (which is unique for each token)
        """
        expire_time = timedelta(**current_app.config['JWT_REFRESH_LIFESPAN'])
        self._redis_blacklist.set(jti,
                                  'blacklisted',
                                  expire_time,
                                  )

    def get(self, key):
        """ Get a key's value from the redis server """
        return self._redis_blacklist.get(key)


jwt_blacklist = BlackList()


# def is_blacklisted(jti):
#     """
#     check whether a JWT token is blacklisted or not.
#
#     This is Flask-Praetorian specific (see guard.init_app() below).
#
#     :param jti: The token's JTI (which is unique for each token)
#     """
#     return jti in jwt_blacklist


def is_blacklisted(jti):
    entry = jwt_blacklist.get(jti)
    # A blacklisted jti has the value 'blacklisted'
    return entry == 'blacklisted'
