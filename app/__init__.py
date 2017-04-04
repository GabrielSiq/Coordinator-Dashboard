#coding: utf-8

from flask import Flask, flash, request
from urlparse import urlparse, urljoin
from urllib2 import urlopen
from flask_user import SQLAlchemyAdapter, UserManager, current_user
import csv
import os
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
from app.members.models import db, User, AcademicData, Role, UserRoles, Query

# Initializes application
application = Flask(__name__)
application.config.from_object("app.config.Config")

# Initializes db
db.init_app(application)

# Defines some global variables
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
DATA_SOURCE = pd.DataFrame()

# Registers user model with db
with application.app_context():

    db.session.query(AcademicData).delete() #Tries to clear previous data from table. For dev. purposes only TODO: Fix this, not working
    db.create_all() # Creates tables defined
    db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model


#TODO: Move these auxiliary functions to a different file
@application.before_first_request
def initialize():
    """
    Initializes our Flask app. Downloads student data and sets up a scheduler to re-download every day.
    """
    # Logic that controls data update not fully implement. updateData() and loadDB() should be commented out except for the first execution. OR, you'd have to clear the academic_data table before restarting the app.
    #updateData()
    loadData()
    #loadDB()
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(updateData, trigger = "interval", days = 1)

def is_safe_url(target):
    """
    Ensures that a redirect target will lead to the same server
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def flash_errors(form):
    """
    Function for debugging errors in forms
    """
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
    """
    #TODO: Temporary solution. Data access will be done primarily through database connection. Not implemented yet, though.
    csv_url = os.path.join(SITE_ROOT, 'static', 'assets', 'data', 'data.csv')
    global DATA_SOURCE
    DATA_SOURCE = pd.read_csv(csv_url, encoding="utf-8")
    DATA_SOURCE.columns = ['matricula', 'periodo', 'disciplina', 'creditos', 'turma', 'grau', 'situacao', 'professor']


def loadDB():
    """
        Loads academic data onto db
    """
    global DATA_SOURCE
    for index, row in DATA_SOURCE.iterrows():
        if row.matricula.isdigit():
            db_row = AcademicData(row.matricula, row.periodo, row.disciplina, row.creditos, row.turma, row.situacao, row.professor, row.grau)
            db.session.add(db_row)
    db.session.commit()

@application.context_processor
def injectDataTable():
    """
    First test of dynamic dashboard building. Does some calculation and parameters depend on saved user preferences.
    Also temporary solution. Data will be dynamically updated via ajax through jquery and not just when the page loads.
    context_processor wrapper allows this function to be accessed from inside the html file.
    """
    def getDataTable(id):
        if id == 1:
            cancellation = DATA_SOURCE[DATA_SOURCE['situacao'].isin(['CA', 'CD', 'CL', 'DT', 'LT'])]
            course_count = DATA_SOURCE.groupby('disciplina').size()
            cancellation = cancellation.groupby('disciplina').size()
            canc_rate = (cancellation / course_count).dropna()

            if current_user.is_authenticated:
                param = Query.query.filter_by(user_id = current_user.id, visualization_id = str(id)).first()
                if param is None:
                    return None
                elif param.query_data['sort'] == 'largest':
                    ascending = False
                else:
                    ascending = True
                return dict(sort = param.query_data['sort'], data = canc_rate.sort_values(ascending=ascending).head(10))
    return dict(getDataTable = getDataTable)

# Hack for modularization
import members.views

# Initialize flask-user
user_manager = UserManager(db_adapter, application,register_view_function = members.views.protected_register)