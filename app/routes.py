from flask import Blueprint, render_template, request, redirect, session, url_for
from .models import Post, User
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