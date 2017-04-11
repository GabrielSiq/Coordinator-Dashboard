# Dashboard Prototype
Development repository for the Coordinator's Dashboard project.

## Quick structure overview
* .ebextensions and .elasticbeanstalk contain AWS deployment-specific information
* app contains most of the useful project files
  * static contains all assets (css, js, img, etc)
  * templates contains our .html files (there are many that aren't being used and are being kepy for reference)
  * members contains our python files
    * models.py contains our models, all of which are present in the database
    * view.py does the routing of urls to the correct views, including data processing prior to displaying
  * init.py contains most initialization logic and temporarily some aux functions
  * config.py contains our application configurations

## Running the project yourself
I haven't tried running this project from a different machine/system but it should work...
1. Basically, the first thing to do is to create a virtual environment with Python 2.7 and installing all of the required packages ($ pip install -r requirements.txt)
2. Then you have to install and set-up a postgres local server. You must modify SQLALCHEMY_DATABASE_URI in config.py. The tables should be automatically created the first time you run the app.
3. The app should run by running (python runserver.py)

Obs: The app takes a while to start when you restart it because it tries to download new data and load it into the database.
For development agility, after everything has been created you can comment out from init.py:
1. Under ```python with application.app_context(): ```, comment out ```python db.drop_all() ```
