from flask import flash, redirect, url_for, render_template, abort, request
from app.members.models import LoginForm, User
from flask_login import login_user, login_required, logout_user
from app import application, is_safe_url
import app

#TODO: load data from database

@application.route('/login', methods=['GET', 'POST'])
def login_func():
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

@application.route('/')
def index():
    return redirect(url_for('dashboard'))

@application.route('/dashboard')
#@login_required
def dashboard():
    DATA_SOURCE = app.DATA_SOURCE

    cancellation = DATA_SOURCE[DATA_SOURCE['situacao'].isin(['CA', 'CD', 'CL', 'DT', 'LT'])]
    course_count = DATA_SOURCE.groupby('disciplina').size()
    cancellation = cancellation.groupby('disciplina').size()
    canc_rate = (cancellation / course_count).dropna()
    return render_template('dashboard.html', df = DATA_SOURCE.head(10).to_dict(), canc = canc_rate.sort_values().head(10), canc2 = canc_rate.sort_values(ascending=False).head(10))

@application.route('/table')
def table():
    DATA_SOURCE = app.DATA_SOURCE
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