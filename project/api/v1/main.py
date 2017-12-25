from flask import Blueprint
from flask_restplus import Api, Resource
from project.core import word

main_api = Blueprint('main_api', __name__)
api = Api(main_api)


@api.route('/')
class Word(Resource):
    def get(self):
        return word
