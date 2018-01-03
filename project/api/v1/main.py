from flask import Blueprint
from flask_restplus import Api, Resource
from project.models import Term, Translation

main_api = Blueprint('main_api', __name__)
api = Api(main_api)


@api.route('/<string:term>')
class TermAPI(Resource):
    def get(self, term):
        term = Term.query.filter_by(term=term.lower()).first_or_404()
        return term.dictionary()
