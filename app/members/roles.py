# Contains our roles names, for easy updating throughout the app


# The Admin can access all parts of our app, add and remove users of all classes, including other ADMINS.
ADMIN_ROLE = "Admin"
# The Coordinator can access most parts of our app, add and remove professors and students within their own departments.
COORDINATOR_ROLE = "Coordinator"
# The Professor can access most parts of our app, add and remove students within their own departments.
PROFESSOR_ROLE = "Professor"
# The Student has restricted access over the app and the data. He can only change his own account.
STUDENT_ROLE = "Student"