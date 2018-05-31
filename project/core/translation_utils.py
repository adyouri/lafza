def translation_is_unique(translation, term):
    """
    Validate that translation is unique for the term

    Meaning that no term should have the same translation twice
    """
    existing_translations = [t.translation for t in term.translations]
    if translation in existing_translations:
        return False
    return True
