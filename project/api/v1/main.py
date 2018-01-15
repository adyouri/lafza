from flask import Blueprint
from flask_restplus import Api, Resource
from sqlalchemy.exc import IntegrityError
from project.models import Term, Translation, db
import project.core as core

main_api = Blueprint('main_api', __name__)
api = Api(main_api)


@api.route('/<string:term>')
class TermAPI(Resource):
    def get(self, term):
        term = Term.query.filter_by(term=term.lower()).first_or_404()
        return term.dictionary()

    def post(self, term):
        term = Term(term=term.lower())
        try:
            db.session.add(term)
            db.session.commit()
        except IntegrityError:
            return {'Error': '{} already exists'.format(term.term),
                    'URL': api.url_for(TermAPI, term=term.term)}, 400
        return term.dictionary(), 201


@api.route('/translations/')
class TranslationsAPI(Resource):
    def get(self):
        all_translations = Translation.query.all()
        return core.translations_repr(all_translations)

    def post(self, translation, term_id):
        translation = Translation(translation=translation, term_id=term_id)
        db.session.add(translation)
        db.session.commit()
        term = Term.query.filter(translation.term_id).first()
        return term.dictionary(), 201
