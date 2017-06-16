import unittest
from passlib.hash import bcrypt
import datetime

from app import application, db
from members.models import User

class TestUser(unittest.TestCase):
    def setUp(self):
        application.config.from_object("app.config.Config")
        with application.app_context():
            db.session.close()

    def test_lookup(self):
        """
        Test creating a new user and saving it to the db. Then, retrieves all users and checks if the new user is there.
        """
        user = User(username="admin", password=bcrypt.hash("password"), email="gabrielsiq@msn.com",
                      confirmed_at=datetime.datetime.now(), is_enabled=True, first_name="Gabriel",
                      last_name="Siqueira", enrollment_number="1234567")
        with application.app_context():
            db.session.add(user)
            db.session.commit()
            users = User.query.all()
            assert user in users
            print "NUMBER OF ENTRIES:"
            print len(users)