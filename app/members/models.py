from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired

# Initializes SQLALchemy
db = SQLAlchemy()

class AcademicData(db.Model):
    """
    Our transcripts/academic data model.
    Each row corresponds to a row in the csv file.
    """
    #TODO: Check if primary key is really consistent. Study possibility of using artificially created ID. (what for?)
    __tablename__ = 'academic_data'

    student_id = db.Column(db.Integer(), primary_key=True)
    semester = db.Column(db.SmallInteger(), primary_key=True)
    course = db.Column(db.String(7), primary_key=True)
    units = db.Column(db.SmallInteger())
    section = db.Column(db.String(3), primary_key=True)
    grade = db.Column(db.Float())
    situation = db.Column(db.String(2), primary_key=True)

    def __init__(self, student_id, semester, course, units, section, situation, professor, grade = None):
        self.student_id = student_id
        self.semester = semester
        self.course = course
        self.units = units
        self.section = section
        self.situation = situation
        self.professor = professor
        self.grade = grade

    def __repr__(self):
        return '<matr {} peri{} disc {} turm {}>'.format(self.student_id, self.semester, self.course, self.section)


class User(db.Model, UserMixin):
    """
    Our User model. Stores basic user info.
    """
    id = db.Column(db.Integer, primary_key=True)

    # User Authentication information
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')

    # User Email information
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    # User information
    is_enabled = db.Column(db.Boolean(), nullable=False, default=False)
    first_name = db.Column(db.String(50), nullable=False, default='')
    last_name = db.Column(db.String(50), nullable=False, default='')

    # Relationships
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))
    departments = db.relationship('Department', secondary='user_departments',
                            backref=db.backref('users', lazy='dynamic'))
    queries = db.relationship('Query', cascade='delete')


    def is_active(self):
      return self.is_enabled

class Query(db.Model):
    """
    First draft model for saving query preferences. Currently links the preferences in json form to a user and a specific element on the dashboard.
    """
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    visualization_id = db.Column(db.String(50), nullable=False)
    query_data = db.Column(db.JSON, nullable=False)
    name = db.Column(db.String(50), nullable=False)

    # Unique names for saved queries from a certain user in a certain visualization
    __table_args__ = (db.UniqueConstraint('user_id', 'visualization_id', 'name', name="_query_uc"),)


class Role(db.Model):
    """
    Role model for authorization.
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    access_level = db.Column(db.Integer()) # To control which roles outrank which.

    def __repr__(self):
        return str(self.id)


class UserRoles(db.Model):
    """
    UserRoles model. Links users and roles.
    """
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'), unique=True) # At this time, only one role is permitted per user, but the structure is here to support more in the future.
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

class Department(db.Model):
    """
    All PUC-Rio departments.
    """
    id  = db.Column(db.Integer(), primary_key=True)
    code = db.Column(db.String(3), unique=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return str(self.id)

class UserDepartments(db.Model):
    """
    Links users and departments
    """
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'), unique=True) # At this time, only one department is permitted per user, but the structure is here to support more in the future.
    department_id = db.Column(db.Integer(), db.ForeignKey('department.id', ondelete='CASCADE'))

# Forms

class ExtraInfo(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    role = SelectField('User Role', coerce=int, validators=[DataRequired()])
    department = SelectField('User Department', coerce=int)

