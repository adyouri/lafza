# Flask-Marshmallow Schemas
from project.models import Term, Translation

from flask_marshmallow import Marshmallow

ma = Marshmallow()


class TranslationSchema(ma.ModelSchema):
    class Meta:
        model = Translation


class TermSchema(ma.ModelSchema):
    class Meta:
        model = Term
    translations = ma.Nested(TranslationSchema, many=True)
