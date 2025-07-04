from flask import Blueprint, request, redirect, render_template, session, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import re

def sanitize_text(text):
    invisible_chars = [
        '\u200B',  # Zero-width space
        '\u200C',  # Zero-width non-joiner
        '\u200D',  # Zero-width joiner
        '\u00A0',  # Non-breaking space
        '\u200E',  # Left-to-right mark
        '\u200F',  # Right-to-left mark
        '\uFEFF',  # Zero-width no-break space (Byte Order Mark)
    ]
    

    for ch in invisible_chars:
        text = text.replace(ch, '')


    text = re.sub(r'\s+', '', text)
    text.replace("‎", "")

    text = re.sub(r'[\u0400-\u04FF]', '', text)

    return text


auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = sanitize_text(request.form['username'])
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(username=username).first():
            return "Username is not available..."
        
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            if user.is_banned:
                return "Account Terminated. your actions on this site have warranted a ban. You are no longer permitted to use this site."
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.feed'))
        return "Invalid creds..."
    
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
