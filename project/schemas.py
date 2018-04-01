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

    @pre_load
    def add_translation_tags(self, data):
        # tags = data['tags']
        # Query Tag() for each tag, create it if it does not exist
        # Return tag_id
        tag_names = data['tags']
        data['tags'] = list(tags_to_tag_ids(tag_names))
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
