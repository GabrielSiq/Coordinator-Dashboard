from flask import Flask, render_template

application = Flask(__name__)


@application.route('/')
def hello_world():
    

    return render_template('dashboard.html')

@application.route('/table')
def table():
    return render_template('table.html')

@application.route('/template')
def template():
    return render_template('template.html')

# @application.errorhandler(404)
# def quatrozeroquatro(e):
#     return render_template('404.html')


if __name__ == '__main__':
    application.run()
