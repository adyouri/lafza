from project.models import Translation, db


def translation_is_unique(translation, term):
    existing_translations = [t.translation for t in term.translations]
    return translation not in existing_translations


def add_translation(translation, term):
    new_translation = Translation(translation=translation, term_id=term.id)
    db.session.add(new_translation)
    term.translations.append(new_translation)
    db.session.commit()


def translations_repr(translations_list):
    ''' Takes a list of translations and returns a list of dictionaries
    containing information for each translation '''
    translations = [{'translation_id': t.id,
                     'translation': t.translation,
                     'created_date': t.created_date.isoformat(),
                     'modified_date': t.modified_date.isoformat(),
                     'score': t.score
                     } for t in translations_list
                    ]
    return translations


def term_repr(term):
    ''' Takes a term instance and returns a dictionary representation'''
    translations = translations_repr(term.translations)
    return {'id': term.id,
            'term': term.term.capitalize(),
            'created_date': term.created_date.isoformat(),
            'translations': translations,
            }


def all_translations():
    translations = Translation.query.all()
    return translations_repr(translations)
