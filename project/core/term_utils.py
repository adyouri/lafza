def validate_full_term_is_acronym(data):
    """ Validate full term exists if is_acronym and is_acronym is not False """
    full_term = data.data.full_term
    is_acronym = data.data.is_acronym

    if full_term and not is_acronym:
        return ('Please set is_acronym to true'
                ' or full_term to null')

    if is_acronym and not full_term:
        return ('Please set is_acronym to false'
                ' or provide full_term')
