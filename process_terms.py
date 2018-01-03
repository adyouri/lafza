from project.models import db, Term, Translation
from app import app
app.app_context().push()

with open('ekalima.md') as f:
    for line in f:
        term, translation, *_ = line.split(' | ')
        term = Term(term=term.lower())
        db.session.add(term)
        translation = Translation(translation=translation.strip('\n'))
        db.session.add(translation)
        term.translations.append(translation)
        db.session.commit()
