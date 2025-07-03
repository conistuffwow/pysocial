from . import db
from werkzeug.utils import secure_filename

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.Text, default="")

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