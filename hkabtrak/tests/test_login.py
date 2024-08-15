import unittest
from werkzeug.security import generate_password_hash
from flask import url_for

from base_test import BaseTestCase, db
from hkabtrak.models import User

class TestLogin(BaseTestCase):

    def setUp(self):
        super().setUp()  # Call the setup from BaseTestCase
        # Create a test user with a hashed password
        self.user = User(
            email='test@example.com',
            password='password123',
            name='Test User',
            user_type='N'
        )
        self.user.password_hash = generate_password_hash('password123')
        db.session.add(self.user)
        db.session.commit()

    def test_login_success(self):
        # Attempt to log in with correct credentials
        response = self.client.post(url_for('staff.staff_login'), data=dict(
            username='test@example.com',
            password='password123'
        ), follow_redirects=True)

        # Check for successful login message
        self.assertIn(b'Login Successful', response.data)

    def test_login_invalid_credentials(self):
        # Attempt to log in with incorrect credentials
        response = self.client.post(url_for('staff.staff_login'), data=dict(
            username='test@example.com',
            password='wrongpassword'
        ), follow_redirects=True)

        # Check for error message
        self.assertIn(b'Invalid credentials. Please try again.', response.data)

    def test_login_redirects_admin(self):
        # Change user type to admin and test redirect
        self.user.user_type = 'A'
        db.session.commit()

        response = self.client.post(url_for('staff.staff_login'), data=dict(
            username='test@example.com',
            password='password123'
        ), follow_redirects=True)

        # Check if redirected to admin main page
        self.assertIn('管理画面'.encode('utf-8'), response.data)


if __name__ == '__main__':
    unittest.main()
