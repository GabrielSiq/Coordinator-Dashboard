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

Obs: The first time you run the app you should uncomment all lines from the initialize() function under app\_init_.py. Then you comment the two previously commented lines back. This is a temporary measure to avoid having to drop the tables every time you restart the app.
