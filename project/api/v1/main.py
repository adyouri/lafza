from flask import Blueprint, json
from flask_restplus import Api, Resource, fields
from sqlalchemy.exc import IntegrityError

from project.models import Term, Translation, Tag, db
from project.schemas import TermSchema, TranslationSchema
# import project.core as core
import project.core.term_utils as term_utils
import project.core.translation_utils as translation_utils
from .users import api as users_api

from flask_praetorian.exceptions import PraetorianError
from flask_praetorian import auth_required, current_user, roles_required

main_api = Blueprint('main_api', __name__)

# Flask-RESTPlus authorization documentation
authorizations = {
        'apiKey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            },
        }

api = Api(main_api, authorizations=authorizations)
api.add_namespace(users_api)


def custom_error_handler(error):
    """
    Custom error handler to use with Flask-Praetorian exceptions.
    Returns the error and the status code for Flask-RESTPlus.
    """
    # Get the error in JSON format
    error_data = error.jsonify()
    # Get a dictionary out of the JSON formatted error
    dictionary_error = json.loads(error_data.get_data())
    # Return the error dictionary and the status code
    return dictionary_error, error_data.status_code


# Handle PraetorianError subclasses using custom_error_handler()
# https://github.com/noirbizarre/flask-restplus/issues/421
for subclass in PraetorianError.__subclasses__():
    subclass_error_handler = api.errorhandler(subclass)
    # This applies the api.errorhandler() decorator to the custom_error_handler
    # just like:
    # @api.errorhandler(subclass)
    # def custom_error_handler: pass
    subclass_error_handler(custom_error_handler)

# Marshmallow schemas
term_schema = TermSchema(
        dump_only=('date_created',
                   'author_id',
                   'author',
                   'translations',
                   )
        )

translation_schema = TranslationSchema(
        dump_only=('date_created',
                   'modified_date',
                   'score',
                   'author_id',
                   'author',
                   'term',
                   ),

        exclude=('downvoters',
                 'upvoters',
                 ),
        )

# Flask-RESTplus Models for documentation
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


@api.route('/terms/', endpoint='terms')
class TermsAPI(Resource):
    method_decorators = [auth_required]

    def get(self):
        """ Get all terms """
        terms = Term.query.all()
        return term_schema.jsonify(terms, many=True)

    @api.expect(term_model)
    def post(self):
        """ Add a new term """
        new_term = term_schema.load(api.payload)

        # Check if there are any marshmallow errors
        # before validating full_term/is_acronym
        if not new_term.errors:
            # Validate full_term/is_acronym
            full_term_error = term_utils.\
                              validate_full_term_is_acronym(new_term)
        else:
            # There are no full_term errors
            full_term_error = False

        # Add full_term/is_acronym error to the new_term errors
        if full_term_error:
            new_term.errors['full_term'] = [full_term_error]

        # Return validation errors
        if new_term.errors:
            return dict(errors=new_term.errors), 400

        # No validation errors, extract the term object
        new_term = new_term.data

        # Assign the current user as the term author
        new_term.author = current_user()

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

        # Term was added, convert to a dictionary and return the data
        result = term_schema.dump(new_term)
        return result.data, 201


@api.route('/terms/<string:term>', endpoint='term')
class TermAPI(Resource):
    def get(self, term):
        """ Get a single term """
        term = Term.query.filter_by(term=term.lower()).first_or_404()
        return term_schema.jsonify(term)


@api.route('/terms/<string:term>', endpoint='delete_term')
class DeleteTermAPI(Resource):
    decorators = [auth_required, roles_required('admin')]

    def delete(self, term):
        """ Delete a term """
        term = Term.query.filter_by(term=term.lower()).first_or_404()
        db.session.delete(term)
        db.session.commit()
        return {'message': 'The term was successfully deleted.'}


@api.route('/translations/<int:translation_id>',
           endpoint='delete_translation')
class DeleteTranslationAPI(Resource):
    decorators = [auth_required]

    def delete(self, translation_id):
        """ Delete a translation """
        translation = Translation.query.get(translation_id)
        db.session.delete(translation)
        db.session.commit()
        return {'message': 'The translation was successfully deleted.'}


@api.route('/tags/<string:tag_name>', endpoint='tag')
class TagAPI(Resource):
    def get(self, tag_name):
        """ Get terms by tranlsation tag """
        # Get the tag
        tag = Tag.query.filter_by(name=tag_name.lower()).first_or_404()
        # Translations with the given tag
        translations = tag.translations
        # A list of the terms that have the translations
        terms = [translation.term for translation in translations]
        return term_schema.jsonify(terms, many=True)


@api.route('/translations/', endpoint='translations')
class TranslationsAPI(Resource):
    method_decorators = [auth_required]

    def get(self):
        """ Get the last 10 added translations """
        translations = Translation.query.order_by(
                Translation.date_created.desc()).limit(10)
        return translation_schema.jsonify(translations, many=True)

    @api.expect(translation_model)
    def post(self):
        """ Add a new translation """
        term = Term.query.get(api.payload['term_id'])
        term_does_not_exist = None
        translation_already_exists = None

        if not term:
            term_does_not_exist = True
        else:
            # Term exists, check that the translation is unique
            is_unique = translation_utils.\
                translation_is_unique(api.payload['translation'], term)

            if not is_unique:
                # Translation is not unique
                translation_already_exists = True

        # Load the API payload to the translation schema
        new_translation = translation_schema.load(api.payload)

        if term_does_not_exist:
            # Add term does not exist error to marshmallow errors
            new_translation.errors['term_id'] = ['Term does not exist']

        if translation_already_exists:
            new_translation.errors['translation'] =\
                    ['Translation already exists']

        if new_translation.errors:
            return dict(errors=new_translation.errors), 400

        # For some reason, assigning the term to the translation is required
        new_translation.data.term = term
        # Assign the current user as the translation author
        new_translation.data.author = current_user()
        # Commit the changes made by `translation_schema.load`
        # This adds the new translation to the database
        db.session.commit()
        # Translation was successfully added, return the term.
        result = term_schema.dump(term)
        return result.data, 201


@api.route('/translations/<int:translation_id>/upvote',
           endpoint='upvote_translation')
class UpvoteTranslationAPI(Resource):
    decorators = [auth_required]

    def get(self, translation_id):
        """ Upvote/Unupvote a translation """
        translation = Translation.query.get(translation_id)

        if current_user() in translation.upvoters:
            # Already upvoted, unupvote translation instead
            translation.upvoters.remove(current_user())
            message = 'The translation was successfully unupvoted.'

        else:
            # Upvote translation
            translation.upvoters.append(current_user())
            message = 'The translation was successfully upvoted.'

        db.session.commit()
        return {'message': message}
