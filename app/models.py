from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5
from flask_login import login_user, current_user, logout_user, login_required



followers = db.Table('follwers', db.Column('followers_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id',db.Integer, db.ForeignKey('user.id')),)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))#foreignkey is used to connect different tables in the database

    def __repr__(self):
        return '<Post {}>'.format(self.body)

@login_required
def user_loader(id):
    return user_loader.query.get(id)
#models are classes used to implement our database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
    followed = db.relationship('User', secondary=followers, primaryjoin=(followers.c.followers_id == id),
                               secondaryjoin=(followers.c.followed_id == id), backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    def followed_post(self):
        followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id).filter
                                                (followers.c.followers_id == self.id).order_by(Post.timestamp.desc()))
        own = Post.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Post.timestamp.desc())



