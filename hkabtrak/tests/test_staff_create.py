# hkabtrak/tests/test_staff_registration.py

from hkabtrak.models import User
from base_test import BaseTestCase, db


class StaffRegistrationTestCase(BaseTestCase):

    def test_staff_registration_new_user(self):
        # Mock login as admin
        with self.client:
            self.login_as_admin()  # Assuming you have a helper to log in as admin

            # Register a new staff user
            response = self.client.post('/staff/staff_register', data={
                'name': 'Test User',
                'email': 'testuser@example.com',
                'password': 'password123'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('スタッフリスト'.encode('utf-8'), response.data)

            # Verify the user was created
            user = User.query.filter_by(email='testuser@example.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.name, 'Test User')
            self.assertTrue(user.check_password('password123'))

    def test_staff_registration_duplicate_email(self):
        # Create an existing user
        user = User(email='existing@example.com', password='password', name='Existing User', user_type='N')
        db.session.add(user)
        db.session.commit()

        # Attempt to register with the same email
        with self.client:
            self.login_as_admin()

            response = self.client.post('/staff/staff_register', data={
                'name': 'New User',
                'email': 'existing@example.com',
                'password': 'newpassword123'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Email already registered', response.data)

    def login_as_admin(self):
        # Create an admin user and log in
        admin = User(email='admin@example.com', password='adminpass', name='Admin User', user_type='A')
        db.session.add(admin)
        db.session.commit()

        self.client.post('/staff/staff_login', data={
            'username': 'admin@example.com',
            'password': 'adminpass'
        })
