from . import db
from werkzeug.utils import secure_filename
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.Text, default="")
    pfp = db.Column(db.String(120), default=None)
    is_banned = db.Column(db.Boolean, default=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(280), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)

    user = db.relationship('User', backref='posts')
    votes = db.relationship('PostVote', backref='post', cascade="all, delete-orphan")


class PostVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    vote = db.Column(db.String(10))

    user = db.relationship('User', backref='post_votes')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='onevote'),
    )

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    user = db.relationship('User', backref='comments')
    post = db.relationship('Post', backref='comments')

class SiteConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=False)

    @staticmethod
    def get(key, default=None):
        setting = SiteConfig.query.filter_by(key=key).first()
        return setting.value if setting else default
    @staticmethod
    def set(key, value):
        setting = SiteConfig.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = SiteConfig(key=key, value=value)
            db.session.add(setting)
        db.session.commit()

    