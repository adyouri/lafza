from flask import Blueprint
from flask_restplus import Api, Resource, fields
from sqlalchemy.exc import IntegrityError
from project.models import Term, Translation, db
import project.core as core
from .users import api as users_api

main_api = Blueprint('main_api', __name__)
api = Api(main_api)
api.add_namespace(users_api)

term_model = api.model('Term', {
                       'term': fields.String,
                       })

translation_model = api.model('Translation', {
                              'translation': fields.String,
                              'term_id': fields.Integer,
                              })


@api.route('/terms/', endpoint='terms')
class TermsAPI(Resource):
    def get(self):
        terms = Term.query.all()
        return [core.term_repr(term) for term in terms]

    @api.expect(term_model)
    def post(self):
        received_term = api.payload['term']
        new_term = Term(term=received_term.lower())

        # Try adding the term
        try:
            db.session.add(new_term)
            db.session.commit()

        # Term already exists in the database
        except IntegrityError:
            db.session.rollback()
            return {'Error': '{} already exists'.format(new_term.term),
                    'URL': api.url_for(TermAPI, term=new_term.term)}, 400

        # Term was added
        return core.term_repr(new_term), 201


@api.route('/terms/<string:term>', endpoint='term')
class TermAPI(Resource):
    def get(self, term):
        term = Term.query.filter_by(term=term.lower()).first_or_404()
        return core.term_repr(term)


@api.route('/translations/', endpoint='translations')
class TranslationsAPI(Resource):
    def get(self):
        all_translations = Translation.query.all()
        return core.translations_repr(all_translations)

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
