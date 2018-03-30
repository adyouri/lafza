# Flask-Marshmallow Schemas
from marshmallow import post_load, pre_dump, validate, pre_load
from project.models import db, Term, Translation

from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import field_for

ma = Marshmallow()


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
        data['tags'] = [1]
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
