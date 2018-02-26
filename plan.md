# Database Plan
Term:

term_id: INTEGER PRIMARY KEY
created_date: DATETIME
term: STRING
translations: TRANSLATION

Translation:

translation_id: INTEGER PRIMARY_KEY
created_date: DATETIME
modified_date: DATETIME
translation: STRING
score: INTEGER
term_id: INTEGER FOREIGN KEY


# Translations API
GET: /1/api/{term} -> Translation
POST: /1/api/{term} <- Translation

GET:
{'term_id': TERM_ID,
 'created_date': CREATED_DATE,
 'term': TERM,
 'translations': [{
                    'translation_id': TRANSLATION_ID,
                    'translation': TRANSLATION,
                    'created_date': CREATED_DATE,
                    'modified_date': MODIFIED_DATE,
                    'score': SCORE
                 }]
}

# How it Should Work

User logs in, adds term, adds translations.
Users vote on translations.
