#coding: utf-8

from flask import Flask, render_template, flash, redirect, url_for, request, abort, Response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from wtforms import StringField, PasswordField, validators
from flask_wtf import FlaskForm
from urlparse import urlparse, urljoin
from urllib2 import urlopen
import csv
import os
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd

application = Flask(__name__)

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

DATA_SOURCE = pd.DataFrame()

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = "login"

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])


# silly user model
class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"


# create some users with ids 1 to 20
users = [User(id) for id in range(1, 21)]


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

@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User(form.username._value())

        login_user(user)

        flash('Logged in successfully.')

        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)

        return redirect(next or url_for('index'))
    return render_template('login.html', form=form)

@application.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(request.referrer)


@application.before_first_request
def initialize():
    """
    Initializes our Flask app. Downloads student data and sets up a scheduler to re-download every day.
    """
    updateData()
    loadData()
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(updateData, trigger = "interval", days = 1)

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

@application.route('/')
def index():
    return redirect(url_for('dashboard'))

@application.route('/dashboard')
@login_required
def dashboard():
    global DATA_SOURCE

    cancelation = DATA_SOURCE[DATA_SOURCE['situacao'].isin(['CA', 'CD', 'CL', 'DT', 'LT'])]
    course_count = DATA_SOURCE.groupby('disciplina').size()
    cancelation = cancelation.groupby('disciplina').size()
    canc_rate = (cancelation / course_count).dropna()
    return render_template('dashboard.html', df = DATA_SOURCE.head(10).to_dict(), canc = canc_rate.sort_values().head(10), canc2 = canc_rate.sort_values(ascending=False).head(10))

@application.route('/table')
def table():
    global DATA_SOURCE
    return render_template('table.html', df = DATA_SOURCE.head(50))

@application.errorhandler(404)
def not_found(error):
     return render_template('404.html')

@application.errorhandler(500)
def server_error(error):
    return render_template('503.html')

@application.errorhandler(503)
def server_error(error):
    return render_template('503.html')

if __name__ == '__main__':
    application.secret_key = 'some secret key'
    application.run()
