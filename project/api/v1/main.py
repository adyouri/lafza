from flask import Blueprint
from flask_restplus import Api, Resource, fields
from sqlalchemy.exc import IntegrityError

from project.models import Term, Translation, Tag, db
from project.schemas import TermSchema, TranslationSchema
# import project.core as core
import project.core.term_utils as term_utils
import project.core.translation_utils as translation_utils
from .users import api as users_api

main_api = Blueprint('main_api', __name__)
api = Api(main_api)
api.add_namespace(users_api)

term_schema = TermSchema(
        dump_only=('date_created',
                   'author_id',
                   'author',
                   'translations')
        )
translation_schema = TranslationSchema(
        dump_only=('date_created',
                   'modified_date',
                   'score',
                   'author_id',
                   'author',
                   'term',
                   )
        )

''' Flask-RESTplus Models for documentation '''
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
                              'tags': fields.List(fields.String),
                              'term_id': fields.Integer,
                              })

''' --END-- Flask-RESTplus Models '''


@api.route('/terms/', endpoint='terms')
class TermsAPI(Resource):
    def get(self):
        terms = Term.query.all()
        return term_schema.jsonify(terms, many=True)

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


@api.route('/terms/<string:term>', endpoint='term')
class TermAPI(Resource):
    def get(self, term):
        term = Term.query.filter_by(term=term.lower()).first_or_404()
        return term_schema.jsonify(term)


@api.route('/tags/<string:tag_name>', endpoint='tag')
class TagAPI(Resource):
    ''' Get terms by tranlsation tags '''
    def get(self, tag_name):
        # Get the tag
        tag = Tag.query.filter_by(name=tag_name.lower()).first_or_404()
        # Translations with the given tag
        translations = tag.translations
        # A list of the terms that have the translations
        terms = [translation.term for translation in translations]
        return term_schema.jsonify(terms, many=True)


@api.route('/translations/', endpoint='translations')
class TranslationsAPI(Resource):
    def get(self):
        translations = Translation.query.all()
        return translation_schema.jsonify(translations, many=True)

    @api.expect(translation_model)
    def post(self):
        term = Term.query.get(api.payload['term_id'])
        term_does_not_exist = None
        translation_already_exists = None

        if not term:
            term_does_not_exist = True
        else:
            is_unique = translation_utils.\
                translation_is_unique(api.payload['translation'], term)

            if not is_unique:
                translation_already_exists = True

        new_translation = translation_schema.load(api.payload)
        if term_does_not_exist:
            new_translation.errors['term_id'] = ['Term does not exist']

        if translation_already_exists:
                new_translation.errors['translation'] =\
                        ['Translation already exists']

        if new_translation.errors:
            return dict(errors=new_translation.errors), 400

        # For some reason, assigning the term to the translation is required
        new_translation.data.term = term
        # Commit the changes made by `translation_schema.load`
        db.session.commit()
        # Translation was successfully added, return the term.
        result = term_schema.dump(term)
        return result.data, 201
