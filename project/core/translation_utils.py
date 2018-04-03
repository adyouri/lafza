from project.models import Term


def validate_translation_uniqueness(translation):
    '''Validate that translation is unique for the term'''
    ''' Meaning that no term should have the same translation twice '''
    term = Term.query.get(translation['term_id'])
    if not term:
        return 'Term does not exist'

    # This is the actual translation string
    translation_string = translation['translation']
    existing_translations = [t.translation for t in term.translations]
    if term and translation_string in existing_translations:
        return 'Translation already exists'
    return False
