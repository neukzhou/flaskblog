from app import db
from datetime import datetime
from sqlalchemy import desc

from webhelpers.date import time_ago_in_words


ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    created = db.Column(db.DateTime)
    # updated = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.title)

    @classmethod
    def all(cls):
        return Post.query.order_by(desc(Post.created)).all()

    @property
    def created_in_words(self):
        return time_ago_in_words(self.created)

    def get_user_id(self):
        return User.query.get( self.user_id ).id
    
    def get_user_name(self):
        return User.query.get( self.user_id ).nickname

    @classmethod
    def get_by_id(cls, id):
        return Post.query.get(id)