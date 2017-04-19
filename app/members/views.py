from flask import redirect, url_for, render_template, request
from flask_user import login_required, roles_required, views as user_views
from app import application, SITE_ROOT
import json
import os
import pandas as pd

#TODO: load data from database

csv_url = os.path.join(SITE_ROOT, 'static', 'assets', 'data', 'data.csv')
DATA = pd.read_csv(csv_url, encoding="utf-8")
DATA.columns = ['matricula', 'periodo', 'disciplina', 'creditos', 'turma', 'grau', 'situacao', 'professor']

@application.route('/')
def index():
    """
    Index view. Currently the dashboard.
    :return: 
    """
    return redirect(url_for('dashboard'))

@application.route('/dashboard')
@login_required
def dashboard():
    """
    Our main dashboard. Does some data processing and renders dashboard view.
    """
    global DATA

    cancellation = DATA[DATA['situacao'].isin(['CA', 'CD', 'CL', 'DT', 'LT'])]
    course_count = DATA.groupby('disciplina').size()
    cancellation = cancellation.groupby('disciplina').size()
    canc_rate = (cancellation / course_count).dropna()
    return render_template('dashboard.html', df = DATA.head(10).to_dict(), canc = canc_rate.sort_values().head(10), canc2 = canc_rate.sort_values(ascending=False).head(10))

@application.route('/table')
@login_required
def table():
    """
    Big table with our academic data. Won't be present in the final product.
    """
    global DATA
    return render_template('table.html', df = DATA.head(50))

@application.errorhandler(404)
def not_found(error):
     return render_template('404.html')

@application.errorhandler(500)
@application.errorhandler(503)
def server_error(error):
    return render_template('503.html')

@roles_required('admin')
def protected_register():
    """
    Registration page is restricted to admins for now. 
    """
    return user_views.register()



@application.route('/rand', methods=['POST'])
@login_required
def rand():
    """
    Testing custom plotting via ajax.
    :return: 
    """
    course = request.json['course']
    global DATA
    filtered = DATA[DATA['disciplina'] == course]['periodo'].value_counts().sort_values()
    data = {}
    data['labels'] =  map(str, filtered.index.values.tolist())
    data['series'] = filtered.values.tolist()

    return json.dumps(data)