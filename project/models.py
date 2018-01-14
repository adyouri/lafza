from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Term(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    term = db.Column(db.String(150), nullable=False, unique=True)
    created_date = db.Column(db.DateTime(),
                             default=datetime.utcnow,
                             nullable=False,
                             )

    def dictionary(self):
        translations = [{"translation": t.translation,
                         "created_date": t.created_date.isoformat(),
                         "modified_date": t.modified_date.isoformat(),
                         "score": t.score
                         } for t in self.translations
                        ]

        return {"id": self.id,
                "term": self.term.capitalize(),
                "created_date": self.created_date.isoformat(),
                "translations": translations,
                }

    def __repr__(self):
        return 'Term: {}'.format(self.term)


class Translation(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    translation = db.Column(db.String(150), nullable=False)
    created_date = db.Column(db.DateTime(),
                             default=datetime.utcnow,
                             nullable=False,
                             )
    modified_date = db.Column(db.DateTime(),
                              default=datetime.utcnow,
                              nullable=False,
                              )
    score = db.Column(db.Integer(), default=1, nullable=False)
    term_id = db.Column(db.Integer(),
                        db.ForeignKey('term.id'),
                        nullable=False)
    term = db.relationship('Term',
                           backref=db.backref('translations', lazy=True),
                           )

    def __repr__(self):
        return 'Translation: {}'.format(self.translation)
