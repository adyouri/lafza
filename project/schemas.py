import project.core.translation_utils as translation_utils
# Flask-Marshmallow Schemas
from marshmallow import post_load, pre_dump, validate, pre_load
from project.models import db, Term, Translation, Tag

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
        #translation_is_unique_error = translation_utils.\
        #                      validate_translation_uniqueness(data)
        ## No errors from marshmallow, check full_term/is_acronym
        #if translation_is_unique_error:
        #    data.errors['translation'] =\
        #            [translation_is_unique_error]
        #    return data
        data = self.add_translation_tags(data)
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

    # Validate term is not none
    # Validate full_term is not none if is_acronym

    @pre_dump()
    def make_acronym(self, data):
        ''' Convert acronyms to uppercase '''
        if data.is_acronym:
            data.term = data.term.upper()
        return data

    @post_load
    def make_term(self, data):
        return data
