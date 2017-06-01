#encoding: utf-8
from flask import redirect, url_for, render_template, request, flash
from flask_user import login_required, roles_required, signals, emails
from flask_user.views import _get_safe_next_param, _send_registered_email, render, _endpoint_url, _do_login_user, quote
from app import application, SITE_ROOT, current_user, getStudentAcademicData, getInstructorEvaluationData, getStudentMappingData
import json
import pandas as pd
from models import *
from datetime import datetime
from roles import ADMIN_ROLE, COORDINATOR_ROLE, PROFESSOR_ROLE, STUDENT_ROLE
import numpy as np

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
    DATA = getUserAllowedData()
    mappingData = getStudentMappingData()

    departments = Department.query.all()

    departmentList = []
    for department in departments:
        entry = {}
        entry[department.id] = department.code
        departmentList.append(entry.copy())

    majorList = mappingData['major'].unique()

    courseCodes = DATA['course'].unique()
    courseCodes.sort()

    situationCodes = DATA['situation'].unique()
    situationCodes.sort()

    previousSemesters = DATA['semester'].unique()
    previousSemesters.sort()

    # TODO: In the future, each class of user would have its own, custom dashboard. I'll leave the structure here but all dashboards point to the same view for now.

    if current_user.has_role(ADMIN_ROLE):
        return render_template('dashboard.html', df=DATA.head(10).to_dict(), course_codes=courseCodes,
                               situation_codes=situationCodes, previous_semesters=previousSemesters,
                               major_list=majorList, department_list=departmentList)
    elif current_user.has_role(COORDINATOR_ROLE):
        return render_template('dashboard.html', df=DATA.head(10).to_dict(), course_codes=courseCodes,
                               situation_codes=situationCodes, previous_semesters=previousSemesters,
                               major_list=majorList, department_list=departmentList)
    elif current_user.has_role(PROFESSOR_ROLE):
        return render_template('dashboard.html', df=DATA.head(10).to_dict(), course_codes=courseCodes,
                               situation_codes=situationCodes, previous_semesters=previousSemesters,
                               major_list=majorList, department_list=departmentList)
    elif current_user.has_role(STUDENT_ROLE):
        return render_template('dashboard.html', df = DATA.head(10).to_dict(), course_codes=courseCodes, situation_codes=situationCodes, previous_semesters = previousSemesters, major_list = majorList, department_list = departmentList)

@application.route('/table')
@roles_required((ADMIN_ROLE, COORDINATOR_ROLE))
@login_required
def table():
    """
    Big table with our academic data. Won't be present in the final product.
    """
    studentData = getUserAllowedData()
    df = pd.DataFrame(columns=studentData.columns)

    instructorData = getInstructorEvaluationData()
    df2 = pd.DataFrame(columns=instructorData.columns)


    return render_template('table.html', df = df, df2=df2)

@application.errorhandler(404)
@application.errorhandler(405)
def not_found(error):
     return render_template('404.html')

@application.errorhandler(500)
@application.errorhandler(503)
def server_error(error):
    return render_template('503.html')


# Registration and User Management

def customRegister():
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

    is_valid, has_expired, user_id = user_manager.verify_token(invite_token, user_manager.invite_expiration)
    if has_expired:
        flash("Your registration token has expired. Please, request a new one.", "error")
        return redirect(url_for('user.login'))

    # require invite without a token should disallow the user from registering
    if user_manager.require_invitation and not invite_token:
        flash("Registration is invite only.", "error")
        return redirect(url_for('user.login'))

    user_invite = None
    if invite_token and db_adapter.UserInvitationClass:
        user_invite = db_adapter.find_first_object(db_adapter.UserInvitationClass, token=invite_token)
        if user_invite and user_invite.user_registered == False:
            register_form.invite_token.data = invite_token
        else:
            flash("Invalid invitation token.", "error")
            return redirect(url_for('user.login'))

    if request.method != 'POST':
        login_form.next.data = register_form.next.data = safe_next
        login_form.reg_next.data = register_form.reg_next.data = safe_reg_next
        if user_invite:
            register_form.email.data = user_invite.email
            register_form.enrollment_number.data = user_invite.enrollment_number

    # Process valid POST
    if request.method == 'POST' and register_form.validate():
        # Create a User object using Form fields that have a corresponding User field
        User = db_adapter.UserClass
        user_class_fields = User.__dict__
        user_fields = {}

        if user_invite.email != register_form.email.data or user_invite.enrollment_number != register_form.enrollment_number.data:
            flash("Email/Enrollment Number don't match invitation.", 'error')
            return redirect(url_for('user.login'))

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

        # Add department and role
        userId = User.query.filter_by(email=register_form.email.data).first().id
        userRole = UserRoles(user_id=userId, role_id=user_invite.role_id)
        db.session.add(userRole)
        userDepartment = UserDepartments(user_id=userId, department_id=user_invite.department_id)
        db.session.add(userDepartment)

        db.session.commit()
        # Send 'registered' email and delete new User object if send fails
        if user_manager.send_registered_email:
            try:
                # Send 'registered' email
                _send_registered_email(user, user_email, require_email_confirmation)
            except Exception as e:
                # delete new User object if send  fails
                db_adapter.delete_object(user)
                db_adapter.commit()
                db.session.remove(userId)
                db.session.remove(userDepartment)
                db.session.commit()
                raise

        # Send user_registered signal
        signals.user_registered.send(current_app._get_current_object(),
                                     user=user,
                                     user_invite=user_invite)

        user_invite.user_registered = True
        db_adapter.commit()

        # Redirect if USER_ENABLE_CONFIRM_EMAIL is set
        if user_manager.enable_confirm_email and require_email_confirmation:
            safe_reg_next = user_manager.make_safe_url_function(register_form.reg_next.data)
            return redirect(safe_reg_next)

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

@login_required
def customInvite():
    """ Allows users to send invitations to register an account """
    user_manager = current_app.user_manager
    db_adapter = user_manager.db_adapter
    extraForm = ExtraInfo()
    roles = Role.query.all()
    extraForm.role.choices = [(role.id, role.name) for role in roles if
                         role.access_level >= max(role.access_level for role in current_user.roles)]
    if not current_user.has_roles(ADMIN_ROLE):
        extraForm.department.choices = [(department.id, department.code) for department in current_user.departments ]
    else:
        extraForm.department.choices = [(department.id, department.code) for department in Department.query.all()]

    invite_form = user_manager.invite_form(request.form)

    if request.method=='POST' and invite_form.validate():
        email = invite_form.email.data
        roleId = extraForm.role.data

        departmentId = extraForm.department.data
        enrollmentNumber = extraForm.enrollment_number.data

        User = db_adapter.UserClass
        user_class_fields = User.__dict__
        user_fields = {
            "email": email
        }

        user, user_email = user_manager.find_user_by_email(email)
        if user:
            flash("User with that email has already registered", "error")
            return redirect(url_for('user.invite'))
        else:
            user_invite = db_adapter \
                            .add_object(db_adapter.UserInvitationClass, **{
                                "email": email,
                                "invited_by_user_id": current_user.id,
                                "role_id": roleId,
                                "department_id": departmentId,
                                "date" : datetime.utcnow(),
                                "enrollment_number" : enrollmentNumber
                            })
        db_adapter.commit()

        token = user_manager.generate_token(user_invite.id)
        accept_invite_link = url_for('user.register',
                                     token=token,
                                     _external=True)

        # Store token
        if hasattr(db_adapter.UserInvitationClass, 'token'):
            user_invite.token = token
            db_adapter.commit()

        try:
            # Send 'invite' email
            inviter = User.query.filter_by(id=user_invite.invited_by_user_id).first()
            inviterName = inviter.first_name + " " + inviter.last_name
            inviteData = {'inviter_name': inviterName, 'invite_link': accept_invite_link}
            emails.send_invite_email(user_invite, inviteData)
        except Exception as e:
            # delete new User object if send fails
            db_adapter.delete_object(user_invite)
            db_adapter.commit()
            raise

        signals \
            .user_sent_invitation \
            .send(current_app._get_current_object(), user_invite=user_invite,
                  form=invite_form)

        flash('Invitation has been sent.', 'success')
        safe_next = _get_safe_next_param('next', user_manager.after_invite_endpoint)
        return redirect(safe_next)

    return render(user_manager.invite_template, form=invite_form, extraForm = extraForm)

@application.route('/user/manageUsers')
@login_required
@roles_required((ADMIN_ROLE, COORDINATOR_ROLE, PROFESSOR_ROLE))
def manageUsers():

    # Gets roles in advance to avoid querying too many times
    allRoles = Role.query.all()

    # Prepares form for editing users
    extraForm = ExtraInfo()
    extraForm.role.choices = [(role.id, role.name) for role in allRoles if
                         role.access_level >= max(role.access_level for role in current_user.roles)]

    roleNames = {}
    for role in allRoles:
        roleNames[role.id] = role.name

    # If user is admin, than he's got access to all users of all departments
    # If user is not admin, he's only got access to users who are members the same departments
    isAdmin = current_user.has_roles(ADMIN_ROLE)

    if isAdmin:
        userDepartments = Department.query.all()
        allUsers = User.query.order_by(User.id.asc()).all()
    else:
        userDepartments = current_user.departments
        allUsers = User.query.filter(User.departments.any(Department.id.in_([department.id for department in userDepartments]))).all()


    extraForm.department.choices = [(department.id, department.code) for department in userDepartments]

    userAccessLevel = max(role.access_level for role in current_user.roles)

    usersList = []
    for user in allUsers:
        targetAccessLevel = max(role.access_level for role in user.roles)
        if isAdmin or userAccessLevel <= targetAccessLevel:
            users = {}
            users['id'] = user.id
            users['first_name'] = user.first_name
            users['last_name'] = user.last_name
            users['email'] = user.email
            role = UserRoles.query.filter_by(user_id=user.id).first().role_id
            users['role'] = roleNames[role]
            users['role_id'] = role
            users['departments'] = user.departments
            users['enrollment_number'] = user.enrollment_number
            usersList.append(users.copy())
    return render_template("users.html", users = usersList, extraForm = extraForm)

@application.route('/user/manageInvites')
@login_required
@roles_required((ADMIN_ROLE, COORDINATOR_ROLE, PROFESSOR_ROLE))
def manageInvites():
    user_manager = current_app.user_manager
    invitedUsers = UserInvitation.query.filter_by(invited_by_user_id = current_user.id).all()
    invitedList = []
    convertedList = []
    for invite in invitedUsers:
        if invite.user_registered:
            userInfo = {}
            userInfo['email'] = invite.email
            userInfo['department'] = Department.query.filter_by(id=invite.department_id).first().code
            userInfo['role'] = Role.query.filter_by(id=invite.role_id).first().name
            userInfo['date'] = User.query.filter_by(email=invite.email).first().confirmed_at.date()
            convertedList.append(userInfo.copy())
        else:
            is_valid, has_expired, user_id = user_manager.verify_token(
                invite.token,
                user_manager.invite_expiration)
            if not has_expired:
                userInfo = {}
                userInfo['id'] = invite.id
                userInfo['email'] = invite.email
                userInfo['department'] = Department.query.filter_by(id=invite.department_id).first().code
                userInfo['role'] = Role.query.filter_by(id=invite.role_id).first().name
                userInfo['date'] = invite.date.date()
                invitedList.append(userInfo.copy())


    return render_template("invites.html", invitedUsers = invitedList, convertedUsers = convertedList)

@application.route('/user/deleteInvite', methods=['POST'])
@login_required
@roles_required((ADMIN_ROLE, COORDINATOR_ROLE, PROFESSOR_ROLE))
def deleteInvite():
    try:
        inviteId = request.form['_inviteId']
    except:
        flash("Parameter error.", "error")
        return redirect(url_for("manageInvites"))

    invite = UserInvitation.query.filter_by(id=inviteId).first()
    if invite:
        if invite.user_registered == True:
            flash("You cannot delete an invite that has been claimed.", "error")
        else:
            try:
                db.session.delete(invite)
                db.session.commit()
            except:
                flash("DB error.", "error")
                return redirect(url_for("manageInvites"))
            flash("Invite succesfully deleted.", "success")
    else:
        flash("Invite not found.", "error")

    return redirect(url_for("manageInvites"))

@application.route('/user/delete', methods=['POST'])
@login_required
@roles_required((ADMIN_ROLE, COORDINATOR_ROLE, PROFESSOR_ROLE))
def deleteUser():
    #TODO: CREATE A LOG TO FIND OUT WHO DELETED WHO
    try:
        userId = request.form['_userId']
    except:
        flash("Parameter error.", "error")
        return redirect(url_for("manageUsers"))

    user = User.query.filter_by(id=userId).first()
    if user:
        if user.id == current_user.id:
            flash("You cannot delete your own account", "error")
        else:
            # Everything related to user is deleted with it (if models are properly set up)
            try:
                db.session.delete(user)
                db.session.commit()
            except:
                flash("DB error.", "error")
                return redirect(url_for("manageUsers"))
            flash("User succesfully deleted.", "success")
    else:
        flash("User not found.", "error")

    return redirect(url_for("manageUsers"))

@application.route('/user/edit', methods=['POST'])
@login_required
@roles_required((ADMIN_ROLE, COORDINATOR_ROLE, PROFESSOR_ROLE))
def editUser():
    #TODO: CREATE A LOG TO FIND OUT WHO CHANGED WHO
    try:
        userId = request.form['_userId']
    except:
        flash("Parameter error.", "error")
        return redirect(url_for("manageUsers"))

    user = User.query.filter_by(id=userId).first()
    if user:
        try:
            user.first_name = request.form['first_name']
            user.last_name = request.form['last_name']
            user.enrollment_number = request.form['enrollment_number']
            if user.email != request.form['email']:
                user.email = request.form['email']
                #TODO: Add email confirmation rotine

            role = UserRoles.query.filter_by(user_id=userId).first()
            role.role_id = request.form['role']

            if Role.query.filter_by(id = role.role_id).first().name == ADMIN_ROLE:
                # If trying to change role to Admin
                if not current_user.has_roles(ADMIN_ROLE):
                    # Only and admin can add another admin
                    flash("Not enough privileges.", "error")
                    return redirect(url_for("manageUsers"))
            else:
                # If trying to add anything else, add department info
                department = UserDepartments.query.filter_by(user_id=userId).first()
                department.department_id = request.form['department']

            db.session.commit()
        except:
            flash("DB error.", "error")
            return redirect(url_for("manageUsers"))
        flash("User succesfully edited.", "success")
    else:
        flash("User not found.", "error")

    return redirect(url_for("manageUsers"))

@application.route('/user/accountInformation')
@login_required
def accountInformation():
    user = User.query.filter_by(id = current_user.id).first()
    role = Role.query.filter_by(id =  str(current_user.roles[0])).first()
    if not current_user.has_roles(ADMIN_ROLE):
        department = Department.query.filter_by(id =  str(current_user.departments[0])).first()
    else:
        department = None

    return render_template('account.html', user=user, role=role, department=department)

@application.route('/user/updateProfile', methods=['POST'])
@login_required
def updateProfile():
    try:
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
    except:
        flash("Parameter error.", "error")
        return redirect(url_for("accountInformation"))

    if email:
        current_user.email = email
        #TODO: ADD ROUTINE TO CONFIRM NEW EMAIL
    if first_name:
        current_user.first_name = first_name
    if last_name:
        current_user.last_name = last_name
    db.session.commit()
    flash("Profile successfully updated!", "success")

    return redirect(url_for("accountInformation"))

# Data providers

def getUserAllowedData():
    data = getStudentAcademicData()
    if not current_user.has_roles((ADMIN_ROLE, COORDINATOR_ROLE)):
        department = Department.query.filter_by(id = str(current_user.departments[0])).first().code
        data = data[data['course'].str.contains(department)]
    return data

@application.route('/getChartData', methods=['POST'])
@login_required
def getChartData():
    """
    Receives request for data, parses the type of view and routes to the correct function.
    """
    if not all(x in request.json for x in ["chartId", "requestParams"]):
        flash("Parameter error", "error")
        return ""
    chartId = request.json['chartId']
    requestParams = request.json['requestParams']

    if chartId in ["enrollment", "enrollment-2"]:
        return getEnrollmentData(requestParams)
    elif chartId in ["cancellation"]:
        return getCancellationData(requestParams)
    elif chartId in ["avg-grade"]:
        return getAverageGradeData(requestParams)
    elif chartId in ["semester-count"]:
        return getStudentSemesterCount(requestParams)
    elif chartId in ["department-breakdown"]:
        return getDepartmentBreakdown(requestParams)
    else:
        flash("Unknown visualization type.", "error")
        return ""

@application.route('/getEnrollmentData', methods=['POST'])
@login_required
def getEnrollmentData(requestParams):
    DATA = getUserAllowedData()

    rowData = {}
    allLabels = []
    for row in requestParams:
        rowData[row] = {}
        filtered = DATA
        # Applies all filters from the request to our data
        rowParams = requestParams[row]
        for key in rowParams:
            if rowParams[key] != "":
                filtered = filtered[filtered[key] == rowParams[key]]

        # Counts number of rows per semester. Outputs in asc order.
        filtered = filtered.groupby('semester').size()

        # Formats the data to return in a dict and converts to json

        rowData[row]['labels'] = filtered.index.values.tolist()

        rowData[row]['series'] = filtered.values.tolist()
        allLabels += list(set(rowData[row]['labels']) - set(allLabels))

    if len(allLabels) != 0:
        allLabels.sort()

        # Now we have to fill in the data with all semesters between the first and last so the year looks full.
        year =  allLabels[0]
        lastYear = allLabels[-1]
        while year <= lastYear:
            if year not in allLabels:
                allLabels.append(year)
            if (year % 10) == 1:
                year += 1
            else:
                year += 9
        allLabels.sort()

    # We then fill the series with null values to match the labels in length
    data = {'labels' : allLabels, 'series' : []}
    for row in rowData:
        fullRow = []
        for label in allLabels:
            if label in rowData[row]['labels']:
                fullRow.append(rowData[row]['series'][rowData[row]['labels'].index(label)])
            else:
                fullRow.append(None)
        data['series'].append(fullRow)

    return json.dumps(data)

@application.route('/getCancellationData', methods=['POST'])
@login_required
def getCancellationData(requestParams):
    DATA = getUserAllowedData()
    filtered = DATA
    onlyRow = requestParams['row0']
    if("sort" not in onlyRow):
        flash("Parameter error.", "error")
        return ""

    cancellation = filtered[filtered['situation'].isin(['CA', 'CD', 'CL', 'DT', 'LT'])]
    course_count = DATA.groupby('course').size()
    cancellation = cancellation.groupby('course').size()
    canc_rate = (cancellation / course_count).dropna()

    return canc_rate.sort_values(ascending=(onlyRow['sort'] == "smallest")).head(10).to_json()

@application.route('/getCancellationData', methods=['POST'])
@login_required
def getAverageGradeData(requestParams):
    DATA = getUserAllowedData()

    rowData = {}
    allLabels = []
    for row in requestParams:
        filtered = DATA
        # Applies all filters from the request to our data
        rowParams = requestParams[row]
        has_filter = False
        for key in rowParams:
            if rowParams[key] != "" and rowParams[key] != None:
                filtered = filtered[filtered[key] == rowParams[key]]
                has_filter = True

        if has_filter == False:
            continue

        # Counts number of rows per semester. Outputs in asc order.
        filtered = filtered[filtered['situation'].isin(['AP', 'RM'])]
        filtered = filtered[['semester', 'grade']]
        filtered = filtered.groupby('semester').mean()

        # Formats the data to return in a dict and converts to json
        rowData[row] = {}
        rowData[row]['labels'] = filtered.index.values.tolist()
        rowData[row]['series'] = filtered.values.flatten().tolist()
        allLabels += list(set(rowData[row]['labels']) - set(allLabels))

    if len(allLabels) != 0:
        allLabels.sort()

        # Now we have to fill in the data with all semesters between the first and last so the year looks full.
        year = allLabels[0]
        while year <= allLabels[-1]:
            if year not in allLabels:
                allLabels.append(year)
            if (year % 10) == 1:
                year += 1
            else:
                year += 9
        allLabels.sort()

    # We then fill the series with null values to match the labels in length
    data = {'labels': allLabels, 'series': []}
    for row in rowData:
        fullRow = []
        for label in allLabels:
            if label in rowData[row]['labels']:
                fullRow.append(rowData[row]['series'][rowData[row]['labels'].index(label)])
            else:
                fullRow.append(None)
        data['series'].append(fullRow)

    return json.dumps(data)

@application.route('/getProfessors', methods=['POST'])
@login_required
def getProfessors():
    data = getUserAllowedData()
    data = data[data['course'] == request.json['course']]
    data = data[pd.notnull(data['professor'])]
    professors = data['professor'].unique().tolist()
    professors.sort()
    return json.dumps(professors)

@application.route('/getStudentDataTable')
@roles_required((ADMIN_ROLE, COORDINATOR_ROLE))
@login_required
def getStudentDataTable():
    data = getUserAllowedData()
    response = {}
    response['draw'] = request.args.get('draw', None)
    response['recordsTotal'] = len(data)
    response['recordsFiltered'] =len(data)
    start =  int(request.args.get('start', None))
    length = int(request.args.get('length', None))
    end = start + length
    listData = []
    for index, row in data[start:end].iterrows():
        listRow = []
        for item in row:
            listRow.append(str(item))
        listData.append(listRow)
    response['data'] = listData
    return json.dumps(response)

@application.route('/getInstructorDataTable')
@roles_required((ADMIN_ROLE, COORDINATOR_ROLE))
@login_required
def getInstructorDataTable():
    data = getInstructorEvaluationData()
    response = {}
    response['draw'] = request.args.get('draw', None)
    response['recordsTotal'] = len(data)
    response['recordsFiltered'] = len(data)
    start =  int(request.args.get('start', None))
    length = int(request.args.get('length', None))
    end = start + length
    listData = []
    for index, row in data[start:end].iterrows():
        listRow = []
        for item in row:
            listRow.append(str(item))
        listData.append(listRow)
    response['data'] = listData
    return json.dumps(response)

@application.route('/getStudentSemesterCount')
@roles_required((ADMIN_ROLE, COORDINATOR_ROLE))
@login_required
def getStudentSemesterCount(requestParams):
    rowData = {}
    allLabels = []

    academicData = getStudentAcademicData()
    majorMapping = getStudentMappingData()
    mergedData = pd.merge(academicData, majorMapping, how='inner', on='student_id')

    for row in requestParams:
        rowData[row] = {}
        # Applies all filters from the request to our data
        rowParams = requestParams[row]
        try:
            semester = rowParams['semester']
        except:
            flash('Parameter error', " error")
            return ""

        if rowParams['major'] != "":
            data = mergedData[mergedData['major'] == rowParams['major']]
        else:
            data = mergedData

        currentStudents = data[(data['semester'] == int(semester)) & ~(data['situation'].isin(['MT', 'CL', 'DT']))][
            'student_id'].unique()
        # get only records that have activity (enrolled students) and limit to prior than the selected semester
        activeSemesters = data[~(data['situation'].isin(['MT', 'CL', 'DT'])) & (data['semester'] <= int(semester))]

        uniqueSemesters = activeSemesters.groupby('student_id')['semester'].unique()
        semesterCount = pd.DataFrame(columns=('Mat', 'Count'))
        for index, semRow in uniqueSemesters.iteritems():
            if index in currentStudents:
                aux = pd.DataFrame([[index, len(semRow)]], columns=('Mat', 'Count'))
                semesterCount = semesterCount.append(aux)

        new = semesterCount.groupby('Count').count()
        rowData[row]['labels'] = new.index.values.tolist()
        rowData[row]['series'] = new['Mat'].tolist()

        allLabels += list(set(rowData[row]['labels']) - set(allLabels))

    if len(allLabels) != 0:
        allLabels.sort()
        # Now we have to fill in the data with all semesters between the first and last so the year looks full.
        count = allLabels[0]
        highestCount = allLabels[-1]
        while count <= highestCount:
            if count not in allLabels:
                allLabels.append(count)
            count += 1
        allLabels.sort()

    # We then fill the series with null values to match the labels in length
    returnData = {'labels': allLabels, 'series': []}
    for row in rowData:
        fullRow = []
        for label in allLabels:
            if label in rowData[row]['labels']:
                fullRow.append(rowData[row]['series'][rowData[row]['labels'].index(label)])
            else:
                fullRow.append(None)
        returnData['series'].append(fullRow)

    return json.dumps(returnData)

@application.route('/getMajorsInDepartment')
@login_required
def getMajorsInDepartment(departmentId):
    #TODO: this function won't be implemented for the first MVP. The stubs here are only for demo purposes.

    # This dict should be replaced by a method for obtaining the majors in all departments
    departmentCourses = {"1" : ["CCP", "CEG", "CSI"]}
    try:
        return departmentCourses[departmentId]
    except:
        raise

@application.route('/getDepartmentBreakdown')
@login_required
def getDepartmentBreakdown(requestParams):
    try:
        departmentId = requestParams['row0']['department']
        semester = requestParams['row0']['semester']
        majors = getMajorsInDepartment(departmentId)
    except:
        flash("Parameter error", "error")
        return ""

    if semester != "":
        academicData = getStudentAcademicData()
        majorMapping = getStudentMappingData()

        currentStudents = academicData[(academicData['semester'] == int(semester)) & ~(academicData['situation'].isin(['MT', 'CL', 'DT']))]['student_id'].unique()

        result = majorMapping[majorMapping['student_id'].isin(currentStudents)]

        data = {'labels':[],'series':[]}
        for major in majors:
            data['labels'].append(major)
            data['series'].append(result[result['major'] == major].shape[0])
        return json.dumps(data)
    else:
        return ""

# Saved queries mechanism

@application.route('/savedQueries', methods=['POST'])
@login_required
def savedQueries():
    """
    Returns a user's saved queries and their parameters for that specific visualization
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

@application.route('/renameQuery', methods=['POST'])
@login_required
def renameQuery():
    try:
        queryName = request.json['query_name']
        queryId = request.json['query_id']
    except:
        flash("Parameter error.", "error")
        return ""
    try:
        query = Query.query.filter_by(id = queryId).first()
        if query.user_id != current_user.id:
            flash("You don't have permissions to alter this query", "error")
            return ""
        query.name = queryName
        db.session.commit()
    except:
        flash("DB error.", "error")
        return ""
    return "success"

@application.route('/saveQuery', methods=['POST'])
@login_required
def saveQuery():
    try:
        visualizationId = request.json['view_id']
        queryName = request.json['query_name']
        queryData = request.json['query_data']
    except:
        flash("Parameter error.", "error")
        return ""
    try:
        query = Query(user_id= current_user.id, visualization_id = visualizationId, name = queryName, query_data = queryData)
        db.session.add(query)
        db.session.commit()
    except:
        flash("DB error.", "error")
        return ""
    return json.dumps(query.id)

@application.route('/deleteQuery', methods=['POST'])
@login_required
def deleteQuery():
    try:
        queryId = request.json['query_id']
    except:
        # Parameter not found. Bad request.
        flash("Parameter error.", "error")
        return ""
    try:
        query = Query.query.filter_by(id=queryId).first()
        db.session.delete(query)
        db.session.commit()
    except:
        # Error when trying to delete from db
        flash("DB error.", "error")
        return ""
    return "success"



