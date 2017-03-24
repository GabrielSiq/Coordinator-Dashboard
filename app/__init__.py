#coding: utf-8

from flask import Flask, render_template, flash, redirect, url_for, request, abort, Response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from urlparse import urlparse, urljoin
from urllib2 import urlopen
from flask_user import SQLAlchemyAdapter, UserManager
import csv
import os
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
from app.members.models import db, User, AcademicData

application = Flask(__name__)
application.config.from_object("app.config.Config")

db.init_app(application)

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

DATA_SOURCE = pd.DataFrame()

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = "login"


with application.app_context():

    db.session.query(AcademicData).delete()
    db.create_all()
    db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
    user_manager = UserManager(db_adapter, application)     # Initialize Flask-User


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

def updateData():
    """
    Updates our student academic transcript data. Currently just grabs the same dummy file for demo purposes. Should be hooked up to an api.
    """
    response = urlopen("https://gist.githubusercontent.com/GabrielSiq/2a592eb7ab47f604ce53cfba6f8191a8/raw/d2560c36b1c98fd74c03ef4d428aed5d7a950efe/historico_anon.csv")
    data = list(csv.reader(response))

    csv_url = os.path.join(SITE_ROOT, 'static', 'assets', 'data', 'data.csv')

    writer = csv.writer(open(csv_url, "w"))
    for row in data:
        writer.writerow(row)

def loadData():
    """
        Loads data onto global variable
        TODO: this needs to change
    """
    csv_url = os.path.join(SITE_ROOT, 'static', 'assets', 'data', 'data.csv')
    global DATA_SOURCE
    DATA_SOURCE = pd.read_csv(csv_url, encoding="utf-8")
    DATA_SOURCE.columns = ['matricula', 'periodo', 'disciplina', 'creditos', 'turma', 'grau', 'situacao', 'professor']
    for index, row in DATA_SOURCE.iterrows():
        if row.matricula.isdigit():
            db_row = AcademicData(row.matricula, row.periodo, row.disciplina, row.creditos, row.turma, row.situacao, row.professor, row.grau)
            db.session.add(db_row)
    db.session.commit()

import members.views