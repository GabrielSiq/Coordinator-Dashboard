#coding: utf-8

from flask import Flask, render_template
from urllib2 import urlopen
import csv
import os
from apscheduler.schedulers.background import BackgroundScheduler

application = Flask(__name__)


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
    response = urlopen("https://gist.githubusercontent.com/GabrielSiq/2a592eb7ab47f604ce53cfba6f8191a8/raw/d2560c36b1c98fd74c03ef4d428aed5d7a950efe/historico_anon.csv")
    data = list(csv.reader(response))

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    csv_url = os.path.join(SITE_ROOT, 'static', 'assets', 'data', 'data.csv')

    writer = csv.writer(open(csv_url, "w"))
    for row in data:
        writer.writerow(row)

@application.route('/')
def hello_world():
    return render_template('dashboard.html')

@application.route('/table')
def table():
    return render_template('table.html')

# @application.errorhandler(404)
# def quatrozeroquatro(e):
#     return render_template('404.html')

if __name__ == '__main__':
    application.run()
