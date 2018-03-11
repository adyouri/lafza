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


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), index=True,
                         nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(50), index=True, nullable=False, unique=True)
    created_date = db.Column(db.DateTime(),
                             default=datetime.utcnow,
                             nullable=False,
                             )
    roles = db.Column(db.String(50))

    @property
    def rolenames(self):
        try:
            return self.roles.split(',')
        except AttributeError:
            return []

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id

    def __repr__(self):
        return 'User: {}'.format(self.username)
