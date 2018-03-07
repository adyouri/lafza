import re

from flask_restplus.fields import String

EMAIL_REGEX = re.compile(r'\S+@\S+\.\S+')


class Email(String):
    '''Email field '''
    __schema_type__ = 'string'
    __schema_format__ = 'email'
    __schema_example__ = 'example@example.com'

    def validate(self, value):
        # Value is None
        if not value:
            return False if self.required else True

        # Email format is incorrect
        if not EMAIL_REGEX.match(value):
            return False

        # Everything else is good
        return True
