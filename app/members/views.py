from flask import redirect, url_for, render_template, request, flash, current_app
from flask_user import login_required, roles_required, signals
from flask_user.views import _get_safe_next_param, _send_registered_email, render, _endpoint_url, _do_login_user, quote
from app import application, SITE_ROOT, current_user
import json
import os
import pandas as pd
from models import *
from datetime import datetime

#TODO: load data from database

csv_url = os.path.join(SITE_ROOT, 'static', 'assets', 'data', 'student_academic_data.csv')
DATA = pd.read_csv(csv_url)
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

    course_codes = DATA['course'].unique()
    course_codes.sort()

    situation_codes = DATA['situation'].unique()
    situation_codes.sort()

    cancellation = DATA[DATA['situation'].isin(['CA', 'CD', 'CL', 'DT', 'LT'])]
    course_count = DATA.groupby('course').size()
    cancellation = cancellation.groupby('course').size()
    canc_rate = (cancellation / course_count).dropna()
    return render_template('dashboard.html', df = DATA.head(10).to_dict(), canc = canc_rate.sort_values().head(10), canc2 = canc_rate.sort_values(ascending=False).head(10), course_codes=course_codes, situation_codes=situation_codes)

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

@application.route('/user/extra/<userId>', methods = ['GET', 'POST'])
@roles_required('Admin')
def extraInformation(userId):
    print userId
    roles = Role.query.all()
    for role in roles:
        print role.id
        print role.name
    form = ExtraInfo()
    form.role.choices = [(role.id, role.name) for role in roles]

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('extra.html', form=form)
        else:
            user = User.query.filter_by(id=userId).one()
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.confirmed_at = datetime.now()

            user_role = UserRoles(user_id=userId, role_id=form.role.data)

            db.session.add(user_role)
            db.session.commit()
            return redirect(url_for('index'))
    elif request.method == 'GET':
        return render_template('extra.html', form=form)


@roles_required('Admin')
def protectedRegister():
    """
    Registration page is restricted to admins for now. 
    """
    """ Display registration form and create new User."""

    user_manager = current_app.user_manager
    db_adapter = user_manager.db_adapter

    safe_next = _get_safe_next_param('next', user_manager.after_login_endpoint)
    safe_reg_next = _get_safe_next_param('next', user_manager.after_register_endpoint)

    # Initialize form
    login_form = user_manager.login_form()  # for login_or_register.html
    register_form = user_manager.register_form(request.form)  # for register.html

    # invite token used to determine validity of registeree
    invite_token = request.values.get("token")

    # require invite without a token should disallow the user from registering
    if user_manager.require_invitation and not invite_token:
        flash("Registration is invite only", "error")
        return redirect(url_for('user.login'))

    user_invite = None
    if invite_token and db_adapter.UserInvitationClass:
        user_invite = db_adapter.find_first_object(db_adapter.UserInvitationClass, token=invite_token)
        if user_invite:
            register_form.invite_token.data = invite_token
        else:
            flash("Invalid invitation token", "error")
            return redirect(url_for('user.login'))

    if request.method != 'POST':
        login_form.next.data = register_form.next.data = safe_next
        login_form.reg_next.data = register_form.reg_next.data = safe_reg_next
        if user_invite:
            register_form.email.data = user_invite.email

    # Process valid POST
    if request.method == 'POST' and register_form.validate():
        # Create a User object using Form fields that have a corresponding User field
        User = db_adapter.UserClass
        user_class_fields = User.__dict__
        user_fields = {}

        # Create a UserEmail object using Form fields that have a corresponding UserEmail field
        if db_adapter.UserEmailClass:
            UserEmail = db_adapter.UserEmailClass
            user_email_class_fields = UserEmail.__dict__
            user_email_fields = {}

        # Create a UserAuth object using Form fields that have a corresponding UserAuth field
        if db_adapter.UserAuthClass:
            UserAuth = db_adapter.UserAuthClass
            user_auth_class_fields = UserAuth.__dict__
            user_auth_fields = {}

        # Enable user account
        if db_adapter.UserProfileClass:
            if hasattr(db_adapter.UserProfileClass, 'active'):
                user_auth_fields['active'] = True
            elif hasattr(db_adapter.UserProfileClass, 'is_enabled'):
                user_auth_fields['is_enabled'] = True
            else:
                user_auth_fields['is_active'] = True
        else:
            if hasattr(db_adapter.UserClass, 'active'):
                user_fields['active'] = True
            elif hasattr(db_adapter.UserClass, 'is_enabled'):
                user_fields['is_enabled'] = True
            else:
                user_fields['is_active'] = True

        # For all form fields
        for field_name, field_value in register_form.data.items():
            # Hash password field
            if field_name == 'password':
                hashed_password = user_manager.hash_password(field_value)
                if db_adapter.UserAuthClass:
                    user_auth_fields['password'] = hashed_password
                else:
                    user_fields['password'] = hashed_password
            # Store corresponding Form fields into the User object and/or UserProfile object
            else:
                if field_name in user_class_fields:
                    user_fields[field_name] = field_value
                if db_adapter.UserEmailClass:
                    if field_name in user_email_class_fields:
                        user_email_fields[field_name] = field_value
                if db_adapter.UserAuthClass:
                    if field_name in user_auth_class_fields:
                        user_auth_fields[field_name] = field_value

        # Add User record using named arguments 'user_fields'
        user = db_adapter.add_object(User, **user_fields)
        if db_adapter.UserProfileClass:
            user_profile = user

        # Add UserEmail record using named arguments 'user_email_fields'
        if db_adapter.UserEmailClass:
            user_email = db_adapter.add_object(UserEmail,
                                               user=user,
                                               is_primary=True,
                                               **user_email_fields)
        else:
            user_email = None

        # Add UserAuth record using named arguments 'user_auth_fields'
        if db_adapter.UserAuthClass:
            user_auth = db_adapter.add_object(UserAuth, **user_auth_fields)
            if db_adapter.UserProfileClass:
                user = user_auth
            else:
                user.user_auth = user_auth

        require_email_confirmation = True
        if user_invite:
            if user_invite.email == register_form.email.data:
                require_email_confirmation = False
                db_adapter.update_object(user, confirmed_at=datetime.utcnow())

        db_adapter.commit()

        # Send 'registered' email and delete new User object if send fails
        if user_manager.send_registered_email:
            try:
                # Send 'registered' email
                _send_registered_email(user, user_email, require_email_confirmation)
            except Exception as e:
                # delete new User object if send  fails
                db_adapter.delete_object(user)
                db_adapter.commit()
                raise

        # Send user_registered signal
        signals.user_registered.send(current_app._get_current_object(),
                                     user=user,
                                     user_invite=user_invite)

        # Redirect if USER_ENABLE_CONFIRM_EMAIL is set
        if user_manager.enable_confirm_email and require_email_confirmation:
            safe_reg_next = user_manager.make_safe_url_function(register_form.reg_next.data)
            return redirect(url_for('extraInformation', userId = user.id))

        # Auto-login after register or redirect to login page
        if 'reg_next' in request.args:
            safe_reg_next = user_manager.make_safe_url_function(register_form.reg_next.data)
        else:
            safe_reg_next = _endpoint_url(user_manager.after_confirm_endpoint)
        if user_manager.auto_login_after_register:
            return _do_login_user(user, safe_reg_next)  # auto-login
        else:
            return redirect(url_for('user.login') + '?next=' + quote(safe_reg_next))  # redirect to login page


    # Process GET or invalid POST
    return render(user_manager.register_template,
                  form=register_form,
                  login_form=login_form,
                  register_form=register_form)

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

@application.route('/getCancellationData', methods=['POST'])
@login_required
def getCancellationData(requestParams):
    global DATA
    filtered = DATA

    if("sort" not in requestParams):
        return ""

    cancellation = filtered[filtered['situation'].isin(['CA', 'CD', 'CL', 'DT', 'LT'])]
    course_count = DATA.groupby('course').size()
    cancellation = cancellation.groupby('course').size()
    canc_rate = (cancellation / course_count).dropna()

    return canc_rate.sort_values(ascending=(requestParams['sort'] == "smallest")).head(10).to_json()




@application.route('/getChartData', methods=['POST'])
@login_required
def getChartData():
    """
    Receives request for data, parses the type of view and routes to the correct function.
    """
    if not all(x in request.json for x in ["chartId", "requestParams"]):
        return ""
    chartId = request.json['chartId']
    requestParams = request.json['requestParams']
    print chartId

    if chartId in ["enrollment", "enrollment-2"]:
        return getEnrollmentData(requestParams)
    elif chartId in ["cancellation"]:
        return getCancellationData(requestParams)
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