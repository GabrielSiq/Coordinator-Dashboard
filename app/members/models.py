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

    def is_active(self):
      return self.is_enabled

