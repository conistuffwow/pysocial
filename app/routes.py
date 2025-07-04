from flask import current_app, flash, Blueprint, render_template, request, abort, redirect, session, url_for
from .models import Post, User, PostVote, Comment, SiteConfig, PostView
from . import db
from config import Config
import os
from werkzeug.utils import secure_filename
from datetime import datetime


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def has_new_comments(post, user_id):
    post_view = PostView.query.filter_by(user_id=user_id, post_id=post.id).first()
    if not post_view:
        return len(post.comments) > 0 
    return any(c.created_at > post_view.last_viewed for c in post.comments)


main = Blueprint('main', __name__)

@main.route('/')
def feed():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('feed.html', posts=posts, has_new_comments=has_new_comments, user_id=session.get('user_id'))

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
    return render_template('profile.html', user=user, has_new_comments=has_new_comments, user_id=session.get('user_id'))

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

@main.route('/uploadpfp', methods=['GET', 'POST'])
def uploadpfp():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        file = request.files.get('pfp')
        if file and allowed_file(file.filename):
            upload_folder = os.path.join(current_app.static_folder, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            filename = secure_filename(f"user_{user.id}_{file.filename}")
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            print(f"Saved to: {filepath}")
            print(f"Assigned to user: {filename}")
            user.pfp = filename
            db.session.commit()
            return redirect(url_for('main.profile', username=user.username))
        else:
            return "Invalid file", 400
        
    return render_template('uploadpfp.html', user=user)

@main.route('/post/<int:post_id>')
def viewpost(post_id):
    post = Post.query.get_or_404(post_id)

    if 'user_id' in session and post.user_id == session['user_id']:
        post_view = PostView.query.filter_by(user_id=session['user_id'], post_id=post_id).first()
        if not post_view:
            post_view = PostView(user_id=session['user_id'], post_id=post_id, last_viewed=datetime.utcnow())
            db.session.add(post_view)
        else:
            post_view.last_viewed = datetime.utcnow()
        db.session.commit()

    return render_template('viewpost.html', post=post)

@main.route('/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    
    content = request.form['content']
    if content.strip():
        comment = Comment(content=content, user_id=user_id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('main.viewpost', post_id=post_id))

@main.route('/admin')
def adminpanel():
    if session.get('username') != "admin":
        abort(403)
    users = User.query.filter(User.username != "admin").all()

    theme_folder = os.path.join(current_app.static_folder, 'themes')
    theme_files = [
        f'themes/{f}' for f in os.listdir(theme_folder)
        if f.endswith('.css')
    ]
    current_theme = SiteConfig.get('theme', 'themes/base.css')
    return render_template('admin.html',
                           users=users,
                           theme_files=theme_files,
                           config_theme=current_theme)

@main.route('/ban/<int:user_id>', methods=['POST'])
def banuser(user_id):
    if session.get('username') != "admin":
        abort(403)
    
    user = User.query.get_or_404(user_id)
    user.is_banned = True
    db.session.commit()
    return redirect(url_for('main.adminpanel'))

@main.route('/settheme', methods=['POST'])
def settheme():
    if session.get('username') != "admin":
        abort(403)
    
    theme = request.form['theme']
    SiteConfig.set('theme', theme)
    return redirect(url_for('main.adminpanel'))

@main.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    users = []
    posts = []

    if query:
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()
        posts = Post.query.filter(Post.content.ilike(f'%{query}%')).all()

    return render_template('search.html', query=query, users=users, posts=posts)

@main.route('/trigger-404')
def trigger_404():
    abort(404)

@main.route('/trigger-500')
def trigger_500():
    abort(500)
