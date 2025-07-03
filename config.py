import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'pictures', 'user')

class Config:
    SECRET_KEY = 'REPLACE THIS PLEASE'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.db')}"
    SQALCHEMY_TRACK_MODIFICATIONS = False