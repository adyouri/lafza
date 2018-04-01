from project.models import Term


def validate_translation_uniqueness(translation):
    '''Validate that translation is unique for the term'''
    ''' Meaning that no term should have the same translation twice '''
    term = Term.query.get(translation.data.term_id)

    # This is the actual translation string (bad naming, should be changed)
    translation_string = translation.data.translation
    existing_translations = [t.translation for t in term.translations]

    if term and translation_string in existing_translations:
        return 'Translation already exists'
