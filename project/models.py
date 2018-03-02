from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
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
    translation = db.Column(db.String(150), nullable=False, unique=True)
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
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(50), index=True, nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime(),
                             default=datetime.utcnow,
                             nullable=False,
                             )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return 'User: {}'.format(self.username)
