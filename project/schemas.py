from marshmallow import pre_dump, validate, pre_load, post_load
from project.models import db, Term, Translation, Tag, User
from project.auth import guard

from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import field_for

ma = Marshmallow()


def tags_to_tag_ids(tags):
    '''A generator that takes a list of string tag names
    and yields IDs of these tags if they exist
    or creates new tags and returns their IDs'''
    for tag_name in tags:
        tag = Tag.query.filter_by(name=tag_name).one_or_none()
        if not tag:
            new_tag = Tag(name=tag_name)
            db.session.add(new_tag)
            db.session.commit()
            yield new_tag.id
        else:
            yield tag.id


class TranslationSchema(ma.ModelSchema):
    term_id = field_for(Translation, 'term_id',
                        required=True,
                        )

    class Meta:
        model = Translation
        sqla_session = db.session

    def add_translation_tags(self, data):
        tag_names = data['tags']
        data['tags'] = list(tags_to_tag_ids(tag_names))
        return data

    @pre_load
    def load_translation(self, data):
        if 'tags' in data.keys() and data['tags']:
            data = self.add_translation_tags(data)
        else:
            data['tags'] = []

        return data


class TermSchema(ma.ModelSchema):
    term = field_for(Term, 'term',
                     required=True,
                     validate=validate.Length(min=2))

    full_term = field_for(Term, 'full_term',
                          validate=validate.Length(min=2))

    # Flask-Marshmallow SQLAlchemy Integration
    class Meta:
        model = Term
    translations = ma.Nested(TranslationSchema, many=True)

    @pre_dump()
    def make_acronym(self, data):
        ''' Convert acronyms to uppercase '''
        if data and data.is_acronym:
            data.term = data.term.upper()
        return data


USERNAME_ERROR = 'Username must be between 3 and 25 characters'
PASSWORD_ERROR = 'Password must be longer than 8 characters'


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User

    username = field_for(User, 'username',
                         required=True,
                         validate=lambda x: len(x) > 3 and len(x) < 25,
                         error_messages={'validator_failed': USERNAME_ERROR},
                         )

    password = field_for(User, 'password',
                         required=True,
                         validate=lambda x: len(x) > 8,
                         error_messages={'validator_failed': PASSWORD_ERROR},
                         load_only=True,
                         )

    email = field_for(User, 'email',
                      required=False,
                      validate=validate.Email(),
                      )

    @post_load
    def encrypt_password(self, data):
        password = data['password']
        data['password'] = guard.encrypt_password(password)
        return data
