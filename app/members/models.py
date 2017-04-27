from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin

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

    # Roles info
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))

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

    queries = db.relationship('User', backref=db.backref('users', lazy='dynamic'))

    # Unique names for saved queries from a certain user in a certain visualization
    __table_args__ = (db.UniqueConstraint('user_id', 'visualization_id', 'name', name="_query_uc"),)


class Role(db.Model):
    """
    Role model for authorization.
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


class UserRoles(db.Model):
    """
    UserRoles model. Links users and roles.
    """
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))
