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
