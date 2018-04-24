from marshmallow import pre_dump, validate, pre_load, post_load
from project.models import db, Term, Translation, Tag, User
from project.auth import guard

from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import field_for

ma = Marshmallow()


def tags_to_tag_ids(tags):
    '''
    A generator that takes a list of string tag names
    and yields IDs of these tags if they exist
    or creates new tags and returns their IDs
    :param: tags: a list of string tag names
    '''
    for tag_name in tags:
        # Query the tag
        tag = Tag.query.filter_by(name=tag_name).one_or_none()
        if not tag:
            # If the tag does not exist, create it and yield the new tag's ID
            new_tag = Tag(name=tag_name)
            db.session.add(new_tag)
            db.session.commit()
            yield new_tag.id
        else:
            # If the tag exists, return it's ID
            yield tag.id


class TranslationSchema(ma.ModelSchema):
    ''' Translation Marshmallow schema '''
    # Make term_id required
    term_id = field_for(Translation, 'term_id',
                        required=True,
                        )
    translation = field_for(Translation, 'translation',
                            required=True,
                            validate=validate.Length(min=2, max=100))

    class Meta:
        '''
            The Flask-Marshmallow Meta class for generating the fields
            directly from SQLAlchemy models
        '''
        model = Translation
        sqla_session = db.session

    def add_translation_tags(self, data):
        ''' A function that adds the tag IDs to the Marshmallow data object '''
        # Save the current tags
        tag_names = data['tags']
        # tags_to_tag_ids() converts the tag names list to a list of tag IDs
        data['tags'] = list(tags_to_tag_ids(tag_names))
        # Return the modified data
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
                     validate=validate.Length(min=2, max=100))

    full_term = field_for(Term, 'full_term',
                          validate=validate.Length(min=2, max=100))

    # Flask-Marshmallow SQLAlchemy integration
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
