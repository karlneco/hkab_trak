# hkabtrak/tests/test_staff_edit.py

from hkabtrak.models import User, Class
from base_test import BaseTestCase, db

class StaffEditTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        # Create a sample admin user
        self.admin_user = User(email='admin@example.com', password='adminpass', name='Admin User', user_type='A')
        db.session.add(self.admin_user)
        db.session.commit()

        # Log in as admin
        self.login_as_admin()

        # Create a sample staff member to edit
        self.staff_user = User(email='staff@example.com', password='staffpass', name='Staff User', user_type='T')
        db.session.add(self.staff_user)
        db.session.commit()

    def login_as_admin(self):
        self.client.post('/staff/staff_login', data={
            'username': 'admin@example.com',
            'password': 'adminpass'
        })

    def test_staff_edit_page_loads(self):
        response = self.client.get(f'/admin/staff/edit/{self.staff_user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Staff', response.data)
        self.assertIn(b'Staff User', response.data)
        self.assertIn(b'staff@example.com', response.data)

    def test_staff_edit_successful(self):
        response = self.client.post(f'/admin/staff/edit/{self.staff_user.id}', data={
            'name': 'Updated Staff User',
            'email': 'updated_staff@example.com',
            'is_active': 'y',
            'user_type': 'H'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('スタッフリスト'.encode('utf-8'), response.data)

        # Verify the staff member was updated
        updated_staff = User.query.get(self.staff_user.id)
        self.assertEqual(updated_staff.name, 'Updated Staff User')
        self.assertEqual(updated_staff.email, 'updated_staff@example.com')
        self.assertTrue(updated_staff.is_active)
        self.assertEqual(updated_staff.user_type, 'H')

    def test_staff_edit_non_existent(self):
        # Log in as the admin user
        self.login_as_admin()

        non_existent_id = self.staff_user.id + 1
        response = self.client.get(f'/admin/staff/edit/{non_existent_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_staff_password_reset(self):
        # Log in as the admin user
        self.login_as_admin()

        new_password = 'newpassword123'
        response = self.client.post(f'/admin/admin/reset_password/{self.staff_user.id}', data={
            'new_password': new_password
        }, follow_redirects=True)

        self.assertEqual(200, response.status_code)
        self.assertIn(b'Password reset successful', response.data)

        # Verify the staff member's password was updated
        updated_staff = User.query.get(self.staff_user.id)
        self.assertTrue(updated_staff.check_password(new_password))



    def tearDown(self):
        super().tearDown()
        # Additional cleanup if needed
