# Flask-Marshmallow Schemas
from project.models import Term, Translation

from flask_marshmallow import Marshmallow

ma = Marshmallow()


class TermSchema(ma.ModelSchema):
    class Meta:
        model = Term


class TranslationSchema(ma.ModelSchema):
    class Meta:
        model = Translation
