from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# many-to-many relationship table | translation.tags / tag.translations
translation_tags = db.Table(
                   'translation_tags',
                   db.Column('translation_id',
                             db.Integer,
                             db.ForeignKey('translation.id'),
                             nullable=False),
                   db.Column('tag_id',
                             db.Integer,
                             db.ForeignKey('tag.id'),
                             nullable=False),

                   db.PrimaryKeyConstraint('translation_id', 'tag_id')
                   )


# Each translation has many upvoters(users)
# Each user has many translations_upvoted
translation_upvoters = db.Table(
                   'translation_upvoters',
                   db.Column('translation_id',
                             db.Integer,
                             db.ForeignKey('translation.id'),
                             nullable=False),
                   db.Column('user_id',
                             db.Integer,
                             db.ForeignKey('user.id'),
                             nullable=False),

                   db.PrimaryKeyConstraint('translation_id', 'user_id')
                   )

# Each translation has many downvoters
# Each user has many translations_downvoted

translation_downvoters = db.Table(
                    'translation_downvoters',
                    db.Column('translation_id',
                              db.Integer,
                              db.ForeignKey('translation.id'),
                              nullable=False),
                    db.Column('user_id',
                              db.Integer,
                              db.ForeignKey('user.id'),
                              nullable=False),

                    db.PrimaryKeyConstraint('translation_id', 'user_id')
                    )


class Term(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    term = db.Column(db.String(150), nullable=False, unique=True)
    is_acronym = db.Column(db.Boolean(), default=False)
    full_term = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(),
                             default=datetime.utcnow,
                             nullable=False,
                             )

    author_id = db.Column(db.Integer(),
                          db.ForeignKey('user.id'),
                          )
    author = db.relationship('User',
                             backref=db.backref('terms', lazy=True),
                             )

    def __repr__(self):
        return 'Term: {}'.format(self.term)


class Translation(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    translation = db.Column(db.String(150), nullable=False)
    date_created = db.Column(db.DateTime(),
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
                           backref=db.backref(
                               'translations',
                               cascade='all, delete-orphan',
                               lazy=True),
                           )

    author_id = db.Column(db.Integer(),
                          db.ForeignKey('user.id'),
                          )
    author = db.relationship('User',
                             backref=db.backref('translations', lazy=True),
                             )
    tags = db.relationship('Tag',
                           secondary=translation_tags,
                           backref=db.backref(
                                              'translations',
                                              lazy='dynamic'),
                           )

    # Each translation has many upvoters(users)
    # Each user has many translations_upvoted
    upvoters = db.relationship('User',
                               secondary=translation_upvoters,
                               backref=db.backref(
                                                  'translations_upvoted',
                                                  lazy='dynamic'),
                               )

    downvoters = db.relationship('User',
                                 secondary=translation_downvoters,
                                 backref=db.backref(
                                                    'translations_downvoted',
                                                    lazy='dynamic'),
                                 )

    def __repr__(self):
        return 'Translation: {}'.format(self.translation)

    def upvote(self, user):
        self.upvoters.append(user)
        self.score += 1

    def unupvote(self, user):
        self.upvoters.remove(user)
        self.score -= 1

    def downvote(self, user):
        self.downvoters.append(user)
        self.score -= 1

    def undownvote(self, user):
        self.downvoters.remove(user)
        self.score += 1

    # NOTE: Should probably just set a score property that returns
    # Upvoters count - Downvoters count


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), index=True,
                         nullable=False, unique=True)
    password = db.Column(db.String(280), nullable=False)
    email = db.Column(db.String(50), index=True, nullable=False, unique=True)
    date_created = db.Column(db.DateTime(),
                             default=datetime.utcnow,
                             nullable=False,
                             )
    roles = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True, server_default='true')

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


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return 'Tag: {}'.format(self.name)
