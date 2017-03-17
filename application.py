#coding: utf-8

from flask import Flask, render_template
from urllib2 import urlopen
import csv
import os
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import numpy as np

application = Flask(__name__)

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

@application.before_first_request
def initialize():
    """
    Initializes our Flask app. Downloads student data and sets up a scheduler to re-download every day.
    """
    updateData()
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

@application.route('/dashboard')
@application.route('/')
def dashboard():
    csv_url = os.path.join(SITE_ROOT, 'static', 'assets', 'data', 'data.csv')
    df = pd.read_csv(csv_url, encoding = "utf-8")
    return render_template('dashboard.html', df = df.head(10).to_dict())

@application.route('/table')
def table():
    return render_template('table.html')

@application.errorhandler(404)
def not_found(error):
     return render_template('404.html')

@application.errorhandler(500)
def server_error(error):
    return render_template('503.html')

if __name__ == '__main__':
    application.run()
