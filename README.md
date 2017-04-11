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
4. The process for creating an admin hasn't been decided yet. For such you should first comment the @roles_required('admin') decorator in the protected_register() function under app\memebers\view.py. Then, you can click the register button at the sign-in page and register an admin and uncomment that line.
5. You need to adjust a few things manually in the database. First, you should add any datetime to the confirmed_at column for the admin you just created. You can also include a name and last name.
6. Then, you go to the roles, table and create a role named Admin (id 1 by default)
7. Lastly, you go to user_roles and add a row with your new user id (probably one) and the role id(probably 1 too.)

Obs: The first time you run the app you should uncomment all lines from the initialize() function under app\_init_.py. Then you comment the two previously commented lines back. This is a temporary measure to avoid having to drop the tables every time you restart the app.
