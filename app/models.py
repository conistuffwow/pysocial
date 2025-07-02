from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(280), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)

    user = db.relationship('User', backref='posts')


class PostVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    vote = db.Column(db.String(10))

    user = db.relationship('User', backref='post_votes')
    post = db.relationship('Post', backref='votes')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='onevote'),
    )