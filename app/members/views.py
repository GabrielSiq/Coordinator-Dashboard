from flask import redirect, url_for, render_template, request
from flask_user import login_required, roles_required, views as user_views
from app import application, SITE_ROOT, current_user
import json
import os
import pandas as pd
from models import Query

#TODO: load data from database

csv_url = os.path.join(SITE_ROOT, 'static', 'assets', 'data', 'data.csv')
DATA = pd.read_csv(csv_url, encoding="utf-8")
DATA.columns = ['student_id', 'semester', 'course', 'units', 'section', 'grade', 'situation', 'professor']

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

    cancellation = DATA[DATA['situation'].isin(['CA', 'CD', 'CL', 'DT', 'LT'])]
    course_count = DATA.groupby('course').size()
    cancellation = cancellation.groupby('course').size()
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

@application.route('/getEnrollmentData', methods=['POST'])
@login_required
def getEnrollmentData(requestParams):
    global DATA
    filtered = DATA

    # Applies all filters from the request to our data
    for key in requestParams:
        if requestParams[key] != "":
            filtered = filtered[filtered[key] == requestParams[key]]

    # Counts number of rows per semester. Outputs in asc order.
    filtered = filtered.groupby('semester').size()

    # Formats the data to return in a dict and converts to json
    data = {}
    data['labels'] = map(str, filtered.index.values.tolist())
    data['series'] = filtered.values.tolist()
    return json.dumps(data)

@application.route('/getChartData', methods=['POST'])
@login_required
def getChartData():
    """
    Receives request for data, parses the type of view and routes to the correct function.
    """
    if not all(x in request.json for x in ["chartId", "requestParams"]):
        return ""
    chartId = request.json['chartId']
    print chartId
    if chartId in ["enrollment", "enrollment-2"]:
        return getEnrollmentData(request.json['requestParams'])
    else:
        return ""


@application.route('/savedQueries', methods=['POST'])
@login_required
def savedQueries():
    """
    Testing custom plotting via ajax.
    :return: 
    """
    data_list = {}
    id = request.json['view_id']

    queries =  Query.query.filter_by(user_id = current_user.id, visualization_id = id).all()
    for query in queries:
        data = {}
        data['name'] = query.name
        data['query_data'] = query.query_data
        data_list[query.id] = data

    return json.dumps(data_list)