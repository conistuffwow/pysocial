from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, url_for
from flask_login import LoginManager, current_user
from config import Config

db = SQLAlchemy()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTS

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)

    db.init_app(app)


    from .routes import main
    from .auth import auth
    app.register_blueprint(main)
    app.register_blueprint(auth)

    @app.context_processor
    def inject_theme():
        from .models import SiteConfig
        theme = SiteConfig.get('theme', 'themes/base.css')
        return {'config_theme': theme}

    with app.app_context():
        db.create_all()
    
    return app

