from flask import Blueprint
from flask_restplus import Api, Resource, fields
from sqlalchemy.exc import IntegrityError

from project.models import Term, Translation, db
from project.schemas import TermSchema, TranslationSchema
import project.core as core
import project.core.term_utils as term_utils
from .users import api as users_api

main_api = Blueprint('main_api', __name__)
api = Api(main_api)
api.add_namespace(users_api)

term_schema = TermSchema()
translation_schema = TranslationSchema()


term_model = api.model('Term', {
                       'term': fields.String(required=True),
                       'is_acronym': fields.Boolean(
                           default=False,
                           required=True
                           ),

                       'full_term': fields.String(
                           example='Full term if is_acronym, null otherwise',
                           default=None,
                           required=True
                           ),
                       })

translation_model = api.model('Translation', {
                              'translation': fields.String,
                              'term_id': fields.Integer,
                              })


@api.route('/terms/', endpoint='terms')
class TermsAPI(Resource):
    def get(self):
        terms = Term.query.all()
        return term_schema.jsonify(terms, many=True)
        # return [core.term_repr(term) for term in terms]

    @api.expect(term_model)
    def post(self):
        new_term = term_schema.load(api.payload)

        # Check if there are any marshmallow errors
        # before validating full_term/is_acronym
        if not new_term.errors:
            full_term_error = term_utils.\
                              validate_full_term_is_acronym(new_term)
        else:
            full_term_error = False

        # No errors from marshmallow, check full_term/is_acronym
        if full_term_error:
            new_term.errors['full_term'] = [full_term_error]

        # Validation errors
        if new_term.errors:
            return dict(errors=new_term.errors), 400
        new_term = new_term.data

        # Try adding the term
        try:
            new_term.term = new_term.term.lower()
            db.session.add(new_term)
            db.session.commit()

        # Term already exists in the database
        except IntegrityError as e:
            db.session.rollback()
            return {'Error': '{} already exists'.format(new_term.term),
                    'URL': api.url_for(TermAPI, term=new_term.term)}, 400

        # Term was added
        result = term_schema.dump(new_term)
        return result.data, 201
        # return core.term_repr(new_term), 201


@api.route('/terms/<string:term>', endpoint='term')
class TermAPI(Resource):
    def get(self, term):
        term = Term.query.filter_by(term=term.lower()).first_or_404()
        return term_schema.jsonify(term)
        # return core.term_repr(term)


@api.route('/translations/', endpoint='translations')
class TranslationsAPI(Resource):
    def get(self):
        translations = Translation.query.all()
        return translation_schema.jsonify(translations, many=True)

    @api.expect(translation_model)
    def post(self):
        received_translation = api.payload['translation']
        received_term_id = api.payload['term_id']
        term = Term.query.get(received_term_id)

        # Check if translation is unique before adding it
        if core.translation_is_unique(translation=received_translation,
                                      term=term):
            core.add_translation(translation=received_translation,
                                 term=term)

        # Translation is not unique
        else:
            return {'Error': '{} already exists'.format(received_translation),
                    'URL': api.url_for(TermAPI, term=term.term)}, 400

        # Translation was added
        return core.term_repr(term), 201
