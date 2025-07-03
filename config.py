import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'REPLACE THIS PLEASE'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.db')}"
    SQALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'pfps')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 # 2mb
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}