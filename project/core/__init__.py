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
