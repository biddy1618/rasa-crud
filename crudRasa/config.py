import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'admin'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_STRING = os.environ['DATABASE_URL_STRING']
    AUTH_CLIENT_ID = os.environ['AUTH_CLIENT_ID']
    AUTH_SECRET = os.environ['AUTH_SECRET']
    AUTH_URL = os.environ['AUTH_URL']


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL_LOCAL']
    SQLALCHEMY_DATABASE_STRING = os.environ['DATABASE_URL_STRING_LOCAL']

class TestingConfig(Config):
    TESTING = True