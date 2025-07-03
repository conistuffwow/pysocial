from flask import flash, Blueprint, render_template, request, abort, redirect, session, url_for
from .models import Post, User, PostVote
from . import db
from config import Config
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024 # two megs of bytes

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTS

main = Blueprint('main', __name__)

@main.route('/')
def feed():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('feed.html', posts=posts, user_id=session.get('user_id'))

@main.route('/post', methods=['POST'])
def post():
    if 'user_id' in session:
        content = request.form['content']
        db.session.add(Post(content=content, user_id=session['user_id']))
        db.session.commit()
    return redirect(url_for('main.feed'))

@main.route('/user/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)

@main.route('/like/<int:post_id>', methods=['POST'])
def like(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('auth.login'))
    
    existing_vote = PostVote.query.filter_by(user_id=user_id, post_id=post.id).first()

    if existing_vote:
        if existing_vote.vote == "like":
            db.session.delete(existing_vote)
            post.likes -= 1
        else:
            existing_vote.vote = "like"
            post.likes += 1
            post.dislikes -= 1
    else:
        vote = PostVote(user_id=user_id, post_id=post_id, vote="like")
        post.likes += 1
        db.session.add(vote)
    
    db.session.commit()
    return redirect(request.referrer or url_for('main.feed'))

@main.route('/dislike/<int:post_id>', methods=['POST'])
def dislike(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('auth.login'))
    
    existing_vote = PostVote.query.filter_by(user_id=user_id, post_id=post.id).first()

    if existing_vote:
        if existing_vote.vote == "dislike":
            db.session.delete(existing_vote)
            post.dislikes -= 1
        else:
            existing_vote.vote = "dislike"
            post.dislikes += 1
            post.likes -= 1
    else:
        vote = PostVote(user_id=user_id, post_id=post_id, vote="dislike")
        post.dislikes += 1
        db.session.add(vote)
    
    db.session.commit()
    return redirect(request.referrer or url_for('main.feed'))

@main.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        abort(403)
    
    post = Post.query.get_or_404(post_id)

    if post.user_id != session['user_id']:
        abort(403)
    
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted :(", "success")
    return redirect(request.referrer or url_for('main.feed'))

@main.route('/editbio', methods=['GET', 'POST'])
def editbio():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.bio = request.form['bio']
        db.session.commit()
        return redirect(url_for('main.profile', username=user.username))
    
    return render_template('editbio.html', user=user)
