from flask import Blueprint, render_template, request, redirect, session, url_for
from .models import Post, User, PostVote
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def feed():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('feed.html', posts=posts)

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