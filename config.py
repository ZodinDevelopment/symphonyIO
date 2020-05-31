import os
basedir = os.path.abspath(os.path.dirname(__file__))
import secrets


class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe()

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'symphony.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    POSTS_PER_PAGE = 10
    TRACKS_PER_PAGE = 5
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    AUDIO_EXTENSIONS = ['wav', 'mp3', 'flac', 'ogg']
    VIDEO_EXTENSIONS = ['mp4', 'webm']

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    ADMINS = ['michael.landon@zodin.dev']


