import unittest
from unittest.mock import patch

from flask import url_for
from werkzeug.security import generate_password_hash

from base_test import BaseTestCase, db
from hkabtrak.models import User


class TestProfile(BaseTestCase):

    def setUp(self):
        super().setUp()
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

    def login(self, username, password):
        return self.client.post(url_for('staff.staff_login'), data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_change_password_success(self):
        # Mock send_email
        self.patcher_send_email = patch('hkabtrak.staff.views.send_email')  # Replace 'your_module' with the actual module name
        self.mock_send_email = self.patcher_send_email.start()

        # Log in as the test user
        self.login('test@example.com', 'password123')

        # Change password with correct current password
        response = self.client.post(url_for('staff.profile'), data=dict(
            current_password='password123',
            new_password='newpassword123',
            confirm_password='newpassword123'
        ), follow_redirects=True)

        # Check for a successful password change message
        self.assertIn(b'Your password has been updated!', response.data)

        # Verify the password was changed in the database
        user = User.query.filter_by(email='test@example.com').first()
        self.assertTrue(user.check_password('newpassword123'))

        # Stop the mock
        self.patcher_send_email.stop()

    def test_change_password_incorrect_current(self):
        # Log in as the test user
        self.login('test@example.com', 'password123')

        # Attempt to change password with incorrect current password
        response = self.client.post(url_for('staff.profile'), data=dict(
            current_password='wrongpassword',
            new_password='newpassword123',
            confirm_password='newpassword123'
        ), follow_redirects=True)

        # Check for an error message indicating incorrect current password
        self.assertIn(b'Current password is incorrect.', response.data)

    def test_change_password_mismatch(self):
        # Log in as the test user
        self.login('test@example.com', 'password123')

        # Attempt to change password with mismatched new passwords
        response = self.client.post(url_for('staff.profile'), data=dict(
            current_password='password123',
            new_password='newpassword123',
            confirm_password='differentpassword'
        ), follow_redirects=True)

        # Check for an error message indicating mismatched passwords
        self.assertIn(b'New passwords do not match.', response.data)


if __name__ == '__main__':
    unittest.main()
