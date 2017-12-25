import datetime

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(150), unique=True, nullable=False)
    date_created = db.Column(db.DateTime(), nullable=False)

    def __init__(self, word, date_created):
        self.word = word
        self.date_created = datetime.datetime.utcnow()

    def __repr__(self):
        return '<Word {}>'.format(self.word)


class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    translation = db.Column(db.String(150), unique=True, nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)
    date_created = db.Column(db.DateTime(), nullable=False)
    word = db.relationship('Word',
                           backref=db.backref('translations', lazy=True)
                           )

    def __init__(self, translation, date_created):
        self.translation = translation
        self.date_created = datetime.datetime.utcnow()

    def __repr__(self):
        return '<Translation {}>'.format(self.translitaion)
