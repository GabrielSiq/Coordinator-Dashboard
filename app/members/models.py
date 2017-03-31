from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin

db = SQLAlchemy()

class AcademicData(db.Model):
    __tablename__ = 'academic_data'

    matricula = db.Column(db.Integer(), primary_key=True)
    periodo = db.Column(db.SmallInteger())
    disciplina = db.Column(db.String(7), primary_key=True)
    creditos = db.Column(db.SmallInteger())
    turma = db.Column(db.String(3))
    grau = db.Column(db.Float())
    situacao = db.Column(db.String(2))
    professor = db.Column(db.String(70))

    def __init__(self, matricula, periodo, disciplina, creditos, turma, situacao, professor, grau = None):
        self.matricula = matricula
        self.periodo = periodo
        self.disciplina = disciplina
        self.creditos = creditos
        self.turma = turma
        self.situacao = situacao
        self.professor = professor
        self.grau = grau

    def __repr__(self):
        return '<matr {} peri{} disc {} turm {}>'.format(self.matricula, self.periodo, self.disciplina, self.turma)


class User(db.Model, UserMixin):
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
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    visualization_id = db.Column(db.String(50), nullable=False)
    query_data = db.Column(db.JSON, nullable=False)

    queries = db.relationship('User', backref=db.backref('users', lazy='dynamic'))

# Define Role model
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define UserRoles model
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))
