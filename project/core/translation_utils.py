from project.models import Term


def validate_translation_uniqueness(translation):
    '''Validate that translation is unique for the term'''
    ''' Meaning that no term should have the same translation twice '''
    term = Term.query.get(translation.data.term_id)
    # No translations
    if not term.translations:
        return None
    elif translation.data.translation in term.translations:
        return 'Translation already exists'
