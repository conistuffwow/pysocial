from flask import Flask, render_template
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
    
    @app.errorhandler(404)
    def notfound(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbiddn(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internalerr(error):
        return render_template('errors/500.html'), 500

    with app.app_context():
        db.create_all()
    
    return app

