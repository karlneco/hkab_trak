from hkabtrak.models import User, Class, staff_class
from base_test import BaseTestCase, db


class StaffDeletionTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        # Create a sample admin user
        self.admin_user = User(email='admin@example.com', password='adminpass', name='Admin User', user_type='A')
        db.session.add(self.admin_user)
        db.session.commit()

        # Log in as admin
        self.login_as_admin()

        # Create a sample staff member to delete
        self.staff_user = User(email='delete_me@example.com', password='deletepass', name='Delete Me', user_type='T')
        db.session.add(self.staff_user)
        db.session.commit()

        # Create a sample class and associate it with the staff member
        self.sample_class = Class(name='Sample Class')
        db.session.add(self.sample_class)
        db.session.commit()

        self.staff_user.classes.append(self.sample_class)
        db.session.commit()

    def test_staff_deletion(self):
        # Ensure the staff member and association exist
        self.assertIsNotNone(User.query.get(self.staff_user.id))
        self.assertIn(self.sample_class, self.staff_user.classes)

        # Delete the staff member
        print(self.staff_user.id)
        response = self.client.post(f'/admin/delete_staff/{self.staff_user.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Staff member deleted successfully', response.data)

        # Verify the staff member was deleted
        self.assertIsNone(User.query.get(self.staff_user.id))

        # Verify that the association between the staff member and class was removed
        result = db.session.execute(
            staff_class.select().where(staff_class.c.user_id == self.staff_user.id)
        ).fetchall()
        self.assertEqual(len(result), 0)

    def test_staff_deletion_non_existent(self):
        # Attempt to delete a non-existent staff member
        non_existent_id = self.staff_user.id + 100
        response = self.client.post(f'/admin/delete_staff/{non_existent_id}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Staff member not found', response.data)

    def tearDown(self):
        super().tearDown()
        # Additional cleanup if needed
