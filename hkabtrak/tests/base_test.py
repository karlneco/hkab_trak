import unittest
from flask_testing import TestCase
from hkabtrak import create_app, db

class BaseTestCase(TestCase):

    def create_app(self):
        # Create the app with test configuration
        app = create_app('test.conf')  # Ensure you have a test configuration file
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database for testing
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing if needed
        return app

    def setUp(self):
        # Set up the test database
        db.create_all()

    def tearDown(self):
        # Tear down the test database
        db.session.remove()
        db.drop_all()

    def login_as_admin(self):
        # Log in as the admin user
        return self.client.post('/staff/staff_login', data=dict(
            username=self.admin_user.email,
            password='adminpass'
        ), follow_redirects=True)