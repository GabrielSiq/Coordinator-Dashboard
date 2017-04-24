import os
basedir = os.path.abspath(os.path.dirname(__file__))
""" 
This files loads all configs for our app
"""
class Config(object):
    """
    Flask Configs
    """
    #TODO: Change secret key (should be in enrivonment variable)
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    """
    SQLALCHEMY CONFIGS
    """
    #SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:database@localhost:5432/prototype"
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:postgres@ebdb.chmuay6n3r4k.sa-east-1.rds.amazonaws.com/ebdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """
    FLASK-USER CONFIGS
    """
    USER_SEND_REGISTERED_EMAIL = False