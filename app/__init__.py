#coding: utf-8

from flask import Flask, flash, request
from urlparse import urlparse, urljoin
from urllib2 import urlopen
from flask_user import SQLAlchemyAdapter, UserManager, current_user
import os
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
from app.members.models import db, User, AcademicData, Role, UserRoles, Query
from passlib.hash import bcrypt
import datetime
import json

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
    #db.drop_all()
    db.create_all() # Creates tables defined
    db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model


#TODO: Move these aux functions to a different file

def createDummyUsers():
    # Test creation of users
    users = list()
    users.append(User(username="admin", password=bcrypt.hash("password"), email="gabrielsiq@msn.com",
                      confirmed_at=datetime.datetime.now(), is_enabled=True, first_name="Gabriel",
                      last_name="Siqueira"))
    users.append(User(username="simone", password=bcrypt.hash("password"), email="simone@inf.puc-rio.br",
                      confirmed_at=datetime.datetime.now(), is_enabled=True, first_name="Simone", last_name="Barbosa"))
    users.append(User(username="noemi", password=bcrypt.hash("password"), email="noemi@inf.puc-rio.br",
                      confirmed_at=datetime.datetime.now(), is_enabled=True, first_name="Noemi", last_name="Rodriguez"))
    for user in users:
        db.session.add(user)

    # Test creation of roles
    roles = list()
    roles.append(Role(name="admin"))
    roles.append(Role(name="base_user"))
    for role in roles:
        db.session.add(role)
    db.session.commit()

    # Test creation of user roles
    user_roles = list()
    user_roles.append(UserRoles(user_id=1, role_id=1))
    user_roles.append(UserRoles(user_id=2, role_id=2))
    user_roles.append(UserRoles(user_id=3, role_id=2))
    for user_role in user_roles:
        db.session.add(user_role)

    # Test creation of saved queries
    queries = list()
    data = {}
    data['sort'] = "largest"
    queries.append(Query(user_id=1, visualization_id=1, query_data=json.dumps(data)))
    data['sort'] = "smallest"
    queries.append(Query(user_id=2, visualization_id=1, query_data=json.dumps(data)))
    queries.append(Query(user_id=3, visualization_id=1, query_data=json.dumps(data)))

    for query in queries:
        db.session.add(query)
    db.session.commit()

@application.before_first_request
def initialize():
    """
    Initializes our Flask app. Downloads student data and sets up a scheduler to re-download every day.
    """

    #updateData()
    loadData(dbOption = False)
    #createDummyUsers()
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
    Updates our student academic transcript data. Currently just grabs the same dummy file and loads into DB for demo purposes. Should be hooked up to an api.
    """
    response = urlopen("https://gist.githubusercontent.com/GabrielSiq/2a592eb7ab47f604ce53cfba6f8191a8/raw/d2560c36b1c98fd74c03ef4d428aed5d7a950efe/historico_anon.csv")
    global DATA_SOURCE
    DATA_SOURCE = pd.read_csv(response)
    DATA_SOURCE.columns = ['matricula', 'periodo', 'disciplina', 'creditos', 'turma', 'grau', 'situacao', 'professor']

    for index, row in DATA_SOURCE.iterrows():
        if row.matricula.isdigit():
            db_row = AcademicData(row.matricula, row.periodo, row.disciplina, row.creditos, row.turma, row.situacao,
                                  row.professor, row.grau)
            db.session.add(db_row)
    db.session.commit()

def loadData(dbOption = False):
    """
        Loads data from stored csv file into global variable and into database. For dev purposes. Not for production.
    """
    csv_url = os.path.join(SITE_ROOT, 'static', 'assets', 'data', 'data.csv')
    global DATA_SOURCE
    DATA_SOURCE = pd.read_csv(csv_url, encoding="utf-8")
    DATA_SOURCE.columns = ['matricula', 'periodo', 'disciplina', 'creditos', 'turma', 'grau', 'situacao', 'professor']
    if(dbOption == True):
        for index, row in DATA_SOURCE.iterrows():
            if row.matricula.isdigit():
                db_row = AcademicData(row.matricula, row.periodo, row.disciplina, row.creditos, row.turma, row.situacao,
                                      row.professor, row.grau)
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
                query = json.loads(param.query_data)
                if param is None:
                    return None
                elif query['sort'] == 'largest':
                    ascending = False
                else:
                    ascending = True
                return dict(sort = query['sort'], data = canc_rate.sort_values(ascending=ascending).head(10))
    return dict(getDataTable = getDataTable)

# Hack for modularization
import members.views

# Initialize flask-user
user_manager = UserManager(db_adapter, application,register_view_function = members.views.protected_register)