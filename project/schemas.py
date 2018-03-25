# Flask-Marshmallow Schemas
from marshmallow import post_load, pre_dump
from project.models import Term, Translation

from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import field_for

ma = Marshmallow()


class TranslationSchema(ma.ModelSchema):
    class Meta:
        model = Translation


class TermSchema(ma.ModelSchema):
    term = field_for(Term, 'term', required=True)

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
