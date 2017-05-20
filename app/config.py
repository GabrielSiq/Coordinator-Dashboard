import os
from members.roles import ADMIN_ROLE, COORDINATOR_ROLE, PROFESSOR_ROLE, STUDENT_ROLE
basedir = os.path.abspath(os.path.dirname(__file__))
""" 
This files loads all configs for our app
"""
class Config(object):
    """
    Flask Configs
    """
    #TODO: Change secret key (should be in enrivonment variables)
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    """
    SQLALCHEMY CONFIGS
    """
    # Local DB
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:database@localhost:5432/prototype"
    # RDS (AWS) DB
    #SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:postgres@ebdb.chmuay6n3r4k.sa-east-1.rds.amazonaws.com/ebdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """
    FLASK-USER CONFIGS
    """
    USER_SEND_REGISTERED_EMAIL = False
    USER_AUTO_LOGIN_AFTER_REGISTER = True
    USER_AFTER_REGISTER_ENDPOINT =  ''
    USER_ENABLE_INVITATION = True
    USER_REQUIRE_INVITATION = True
    USER_INVITE_ENDPOINT = 'manageUsers'

    # User roles for Jinja

    ADMIN_ROLE = ADMIN_ROLE
    COORDINATOR_ROLE = COORDINATOR_ROLE
    PROFESSOR_ROLE = PROFESSOR_ROLE
    STUDENT_ROLE = STUDENT_ROLE

    """
    FLASK-MAIL CONFIGS
    """
    MAIL_SERVER = "smtp-mail.outlook.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "gabrielsiq@msn.com"
    MAIL_PASSWORD = "Analuiza2005!"
    MAIL_DEFAULT_SENDER = "gabrielsiq@msn.com"

