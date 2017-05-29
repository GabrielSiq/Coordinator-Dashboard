#encoding: utf-8

from flask import Flask, flash, request
from urlparse import urlparse, urljoin
from urllib2 import urlopen, URLError
from flask_user import SQLAlchemyAdapter, UserManager, current_user
import os
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
from members.models import db, User, AcademicData, Role, UserRoles, Query, Department, UserDepartments, StudentMajorMapping, InstructorEvaluationData, UserInvitation, CustomRegisterForm
from passlib.hash import bcrypt
import datetime
import json
from wtforms import ValidationError
from members.roles import ADMIN_ROLE, COORDINATOR_ROLE, PROFESSOR_ROLE, STUDENT_ROLE
import math
from flask_mail import Mail

# Initializes application
application = Flask(__name__)
application.config.from_object("app.config.Config")

# Initializes db
db.init_app(application)

# Defines some global variables
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
STUDENT_ACADEMIC_DATA = pd.DataFrame()
STUDENT_MAPPING_DATA = pd.DataFrame()
INSTRUCTOR_EVALUATION_DATA = pd.DataFrame()

# Registers user model with db
with application.app_context():
    db.drop_all()
    db.create_all() # Creates tables defined
    db_adapter = SQLAlchemyAdapter(db, User, UserInvitationClass=UserInvitation)        # Register the User model


#TODO: Move these aux functions to a different file

@application.before_first_request
def initialize():
    """
    Initializes our Flask app. Downloads student data and sets up a scheduler to re-download every day.
    """

    #updateData()
    loadData(dbOption = False)
    createDummyUsers()
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(updateData, trigger = "interval", days = 1)

def getStudentAcademicData():
    global STUDENT_ACADEMIC_DATA
    return STUDENT_ACADEMIC_DATA

def getStudentMappingData():
    global STUDENT_MAPPING_DATA
    return STUDENT_MAPPING_DATA

def getInstructorEvaluationData():
    global INSTRUCTOR_EVALUATION_DATA
    return INSTRUCTOR_EVALUATION_DATA

def createDummyUsers():
    # Test creation of users
    users = list()
    users.append(User(username="admin", password=bcrypt.hash("password"), email="gabrielsiq@msn.com",
                      confirmed_at=datetime.datetime.now(), is_enabled=True, first_name="Gabriel",
                      last_name="Siqueira", enrollment_number="1234567"))
    users.append(User(username="simone", password=bcrypt.hash("password"), email="gdssiqueira@gmail.com",
                      confirmed_at=datetime.datetime.now(), is_enabled=True, first_name="Simone", last_name="Barbosa", enrollment_number="1234568"))
    users.append(User(username="noemi", password=bcrypt.hash("password"), email="gdssiqueira@umail.ucsb.edu",
                      confirmed_at=datetime.datetime.now(), is_enabled=True, first_name="Noemi", last_name="Rodriguez", enrollment_number="1234569"))
    users.append(User(username="johndoe", password=bcrypt.hash("password"), email="gdssiqueira@cs.ucsb.edu",
                      confirmed_at=datetime.datetime.now(), is_enabled=True, first_name="John", last_name="Doe", enrollment_number="1234560"))
    for user in users:
        db.session.add(user)

    # Test creation of roles
    roles = list()
    roles.append(Role(name = ADMIN_ROLE, access_level = 0))
    roles.append(Role(name = COORDINATOR_ROLE, access_level = 1))
    roles.append(Role(name = PROFESSOR_ROLE, access_level = 2))
    roles.append(Role(name = STUDENT_ROLE, access_level = 5))
    for role in roles:
        db.session.add(role)

    departments = list()
    departments.append(Department(code="INF", name="Departamento de Informatica"))
    departments.append(Department(code="MAT", name="Departamento de Matematica"))
    departments.append(Department(code="ENG"))

    for department in departments:
        db.session.add(department)

    db.session.commit()

    # Test creation of user roles
    user_roles = list()
    user_roles.append(UserRoles(user_id=1, role_id=1))
    user_roles.append(UserRoles(user_id=2, role_id=3))
    user_roles.append(UserRoles(user_id=3, role_id=2))
    user_roles.append(UserRoles(user_id=4, role_id=4))
    for user_role in user_roles:
        db.session.add(user_role)

    user_departments = list()
    user_departments.append(UserDepartments(user_id=2, department_id = 1))
    user_departments.append(UserDepartments(user_id=3, department_id=2))
    user_departments.append(UserDepartments(user_id=4, department_id=1))
    for user_department in user_departments:
        db.session.add(user_department)

    # Test creation of saved queries
    queries = list()
    data = {}
    row = {}

    row['sort'] = "largest"
    data['row0'] = row.copy()
    queries.append(Query(user_id=1, visualization_id="cancellation", query_data=json.dumps(data), name="abc"))
    row['sort'] = "smallest"
    data['row0'] = row.copy()
    queries.append(Query(user_id=2, visualization_id="cancellation", query_data=json.dumps(data), name="abc"))
    queries.append(Query(user_id=3, visualization_id="cancellation", query_data=json.dumps(data), name="abc"))

    data = {}
    row = {}
    row['course'] = "INF1007"
    row['situation'] = 'AP'
    data['row0'] = row.copy()
    row['course'] = "INF1007"
    row['situation'] = 'RM'
    data['row1'] = row.copy()
    queries.append(Query(user_id=1, visualization_id="enrollment", query_data=json.dumps(data), name="Prog 2 - Approved + Failed"))
    row['course'] = "INF1005"
    row['situation'] = 'RM'
    data['row0'] = row.copy()
    queries.append(Query(user_id=1, visualization_id="enrollment", query_data=json.dumps(data), name="Prog 1 - Failed (grade)"))
    row['course'] = "INF1403"
    row['situation'] = 'RF'
    data['row0'] = row.copy()
    queries.append(Query(user_id=1, visualization_id="enrollment", query_data=json.dumps(data), name="HCI - Failed (attendance)"))
    queries.append(Query(user_id=1, visualization_id="enrollment-2", query_data=json.dumps(data), name="HCI - Failed (attendance)"))
    row['course'] = "INF1009"
    row['situation'] = ''
    data['row0'] = row.copy()
    queries.append(Query(user_id=1, visualization_id="enrollment-2", query_data=json.dumps(data), name="Logics - All"))

    for query in queries:
        db.session.add(query)
    db.session.commit()

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

# Update functions

def getUpdatedAcademicData(fromDb = False):
    global STUDENT_ACADEMIC_DATA
    if fromDb == True:
        try:
            STUDENT_ACADEMIC_DATA =  pd.read_sql_query(AcademicData.query.statement, db.session.bind)
        except:
            #TODO: LOG UPDATE FAIL
            raise
    else:
        try:
            response = urlopen(
                "https://gist.githubusercontent.com/GabrielSiq/cfa8822fe87ae5ac40b1a944ac791447/raw/07a5e12a9f9bfce3aa60cb24e6c6efeed0abd32c/student_academic_data.csv")
            STUDENT_ACADEMIC_DATA = pd.read_csv(response)
        except URLError:
            #TODO: LOG UPDATE FAIL
            raise
    STUDENT_ACADEMIC_DATA.columns = ['student_id', 'semester', 'course', 'units', 'section', 'grade',
                                             'situation', 'professor']
    #TODO: LOG UPDATE SUCCESSFUL

def persistAcademicData():
    global STUDENT_ACADEMIC_DATA
    AcademicData.query.delete()
    for index, row in STUDENT_ACADEMIC_DATA.iterrows():
        db_row = AcademicData(row.student_id, row.semester, row.course, row.units, row.section, row.situation,
                              row.professor, row.grade)
        db.session.add(db_row)
    db.session.commit()

def getUpdatedMappingData(fromDb = False):
    global STUDENT_MAPPING_DATA
    if fromDb == True:
        try:
            STUDENT_MAPPING_DATA =  pd.read_sql_query(StudentMajorMapping.query.statement, db.session.bind)
        except:
            #TODO: LOG UPDATE FAIL
            raise
    else:
        try:
            response = urlopen(
                "https://gist.githubusercontent.com/GabrielSiq/4512611d24ee4aefbd7c2ce72a70706d/raw/ada394ba2ae678a302f0c3eaa127670622fd9961/student_major_mapping.csv")
            STUDENT_MAPPING_DATA = pd.read_csv(response)
        except URLError:
            #TODO: LOG UPDATE FAIL
            raise

    STUDENT_MAPPING_DATA.columns = ['student_id', 'major']
    #TODO: LOG UPDATE SUCCESSFUL

def persistMappingData():
    global STUDENT_MAPPING_DATA
    StudentMajorMapping.query.delete()
    for index, row in STUDENT_MAPPING_DATA.iterrows():
        db_row = StudentMajorMapping(row.student_id, row.major)
        db.session.add(db_row)

    db.session.commit()

def getUpdatedEvaluationData(fromDb = False):
    global INSTRUCTOR_EVALUATION_DATA
    if fromDb == True:
        try:
            INSTRUCTOR_EVALUATION_DATA =  pd.read_sql_query(InstructorEvaluationData.query.statement, db.session.bind)
        except:
            #TODO: LOG UPDATE FAIL
            raise
    else:
        try:
            response = urlopen(
                "https://gist.githubusercontent.com/GabrielSiq/6e5574a42be340121bceed955dd5201b/raw/b4e88380f0235880656c2dfca75c98cfea0e8ef6/instructor_evaluation_data.csv")
            INSTRUCTOR_EVALUATION_DATA = pd.read_csv(response)
        except URLError:
            #TODO: LOG UPDATE FAIL
            raise

    INSTRUCTOR_EVALUATION_DATA.columns = ["semester", "course", "section", "professor", "student_count", "question_text", "grade_1", "grade_2", "grade_3", "grade_4", "grade_5", "grade_na", "average", "standard_deviation", "total"]
    #TODO: LOG UPDATE SUCCESSFUL

def persistEvaluationData():
    global INSTRUCTOR_EVALUATION_DATA
    InstructorEvaluationData.query.delete()
    for index, row in INSTRUCTOR_EVALUATION_DATA.iterrows():
        if not math.isnan(row.student_count):
            db_row = InstructorEvaluationData(row.semester, row.course, row.section, row.professor, row.student_count, row.question_text, row.grade_1, row.grade_2, row.grade_3, row.grade_4, row.grade_5, row.grade_na, row.average, row.standard_deviation)
            db.session.add(db_row)
            db.session.commit()

    db.session.commit()

def updateData():
    """
    Updates our student academic transcript data. Currently just grabs the same dummy file and loads into DB for demo purposes. Should be hooked up to an api.
    """
    # Update student academic data
    try:
        getUpdatedAcademicData()
        persistAcademicData()
    except URLError:
        getUpdatedAcademicData(fromDb = True)

    # Update student mapping data
    try:
        getUpdatedMappingData()
        persistMappingData()
    except URLError:
        getUpdatedMappingData(fromDb = True)

    # Update instructor evaluation data
    try:
        getUpdatedEvaluationData()
        persistEvaluationData()
    except URLError:
        getUpdatedEvaluationData(fromDb = True)

def loadData(dbOption = False):
    """
        Loads data from stored csv file into global variable and into database. For dev purposes. Not for production.
    """
    csv_url = os.path.join(SITE_ROOT, 'static', 'assets', 'data', 'student_academic_data.csv')
    global STUDENT_ACADEMIC_DATA
    STUDENT_ACADEMIC_DATA = pd.read_csv(csv_url)
    STUDENT_ACADEMIC_DATA.columns = ['student_id', 'semester', 'course', 'units', 'section', 'grade', 'situation', 'professor']
    for index, row in STUDENT_ACADEMIC_DATA.iterrows():
        if str(row.student_id)[3] == "0":
            STUDENT_ACADEMIC_DATA.set_value(index, 'curriculum', "0")
        else:
            STUDENT_ACADEMIC_DATA.set_value(index, 'curriculum', "1")


    csv_url = os.path.join(SITE_ROOT, 'static', 'assets', 'data', 'instructor_evaluation_data.csv')
    global INSTRUCTOR_EVALUATION_DATA
    INSTRUCTOR_EVALUATION_DATA = pd.read_csv(csv_url)
    INSTRUCTOR_EVALUATION_DATA.columns = ["semester", "course", "section", "professor", "student_count", "question_text", "grade_1", "grade_2", "grade_3", "grade_4", "grade_5", "grade_na", "average", "standard_deviation", "total"]
    del INSTRUCTOR_EVALUATION_DATA['total']
    del INSTRUCTOR_EVALUATION_DATA['question_text']

    if(dbOption == True):
        for index, row in STUDENT_ACADEMIC_DATA.iterrows():
            db_row = AcademicData(row.student_id, row.semester, row.course, row.units, row.section, row.situation,
                                  row.professor, row.grade)
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
        if id == "cancellation":
            cancellation = STUDENT_ACADEMIC_DATA[STUDENT_ACADEMIC_DATA['situation'].isin(['CA', 'CD', 'CL', 'DT', 'LT'])]
            course_count = STUDENT_ACADEMIC_DATA.groupby('course').size()
            cancellation = cancellation.groupby('course').size()
            canc_rate = (cancellation / course_count).dropna()

            if current_user.is_authenticated:
                param = Query.query.filter_by(user_id = current_user.id, visualization_id = str(id)).first()

                if param is None:
                    return None
                else:
                    query = json.loads(param.query_data)['row0']
                    if query['sort'] == 'largest':
                        ascending = False
                    else:
                        ascending = True
                return dict(sort = query['sort'], data = canc_rate.sort_values(ascending=ascending).head(10))
    return dict(getDataTable = getDataTable)

def my_password_validator(form, field):
    password = field.data
    if len(password) < 3:
        raise ValidationError('Password must have at least 3 characters')

# Initializing Flask-Mail
mail = Mail(application)

# Hack for modularization
import members.views

# Initialize flask-user
user_manager = UserManager(db_adapter, application,register_view_function = members.views.customRegister, invite_view_function = members.views.customInvite, password_validator=my_password_validator, register_form = CustomRegisterForm)