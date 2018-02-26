from flask import Blueprint
from flask_restplus import Api, Resource, fields
from sqlalchemy.exc import IntegrityError
from project.models import Term, Translation, db
import project.core as core

main_api = Blueprint('main_api', __name__)
api = Api(main_api)

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
        return [term.dictionary() for term in terms]

    @api.expect(term_model)
    def post(self):
        print(api.payload)
        received_term = api.payload['term']
        term = Term(term=received_term.lower())
        try:
            db.session.add(term)
            db.session.commit()
        except IntegrityError:
            return {'Error': '{} already exists'.format(term.term),
                    'URL': api.url_for(TermAPI, term=term.term)}, 400
        return term.dictionary(), 201


@api.route('/terms/<string:term>', endpoint='term')
class TermAPI(Resource):
    def get(self, term):
        term = Term.query.filter_by(term=term.lower()).first_or_404()
        return term.dictionary()


@api.route('/translations/', endpoint='translations')
class TranslationsAPI(Resource):
    def get(self):
        all_translations = Translation.query.all()
        return core.translations_repr(all_translations)

    @api.expect(translation_model)
    def post(self):
        received_translation = api.payload['translation']
        received_term_id = api.payload['term_id']
        new_translation = Translation(translation=received_translation,
                                      term_id=received_term_id)
        db.session.add(new_translation)
        db.session.commit()
        term = Term.query.get(new_translation.term_id)
        term.translations.append(new_translation)
        return term.dictionary(), 201
