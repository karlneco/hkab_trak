import unittest
from unittest.mock import patch, MagicMock
from flask import url_for

from hkabtrak.absences.views import record_absence
from hkabtrak.models import Absence, Class
from base_test import BaseTestCase, db


class TestRecordAbsenceUnit(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.populate_test_data()

    def populate_test_data(self):
        """Insert test data into the database."""
        test_class = Class(id=1, name="Grade 2", instructions="Test instructions")
        db.session.add(test_class)
        db.session.commit()

    @patch('hkabtrak.absences.views.Class.query')
    @patch('hkabtrak.absences.views.db.session.add')
    @patch('hkabtrak.absences.views.db.session.commit')
    @patch('hkabtrak.absences.views.send_absence_notification')
    def test_record_absence_form_validation_error(self, mock_send_email, mock_db_commit, mock_db_add, mock_class_query):
        """Test form validation failure (unit test)."""

        with self.client:  # Use Flask test client
            response = self.client.post(url_for('absences.record_absence'), data={})  # Missing required fields

        # Ensure validation fails and returns the absence form template
        self.assertEqual(response.status_code, 200)  # Form should re-render
        self.assertIn(b"Error in", response.data)  # Check for error messages

        # Ensure absence is NOT added to the database
        mock_db_add.assert_not_called()
        mock_db_commit.assert_not_called()
        mock_send_email.assert_not_called()

    @patch('hkabtrak.absences.views.Class.query')
    @patch('hkabtrak.absences.views.db.session.add')
    @patch('hkabtrak.absences.views.db.session.commit')
    @patch('hkabtrak.absences.views.send_absence_notification')
    def test_record_absence_success(self, mock_send_email, mock_db_commit, mock_db_add, mock_class_query):
        """Test successful absence submission (unit test)."""

        mock_class = MagicMock()
        mock_class.id = 1
        mock_class.name = "Grade 2"
        mock_class.staff = [MagicMock(email="teacher@example.com")]
        mock_class_query.get.return_value = mock_class
        mock_class_query.all.return_value = [mock_class]

        form_data = {
            'parent_email': 'parent@example.com',
            'class_id': 1,
            'student_name': 'Test Student',
            'absence_type': '欠席',
            'reason': '体調不良',
            'date': '2025-03-14',
            'start_time': '08:00',
            'end_time': '12:00',
            'comment': 'Not feeling well',
            'g-recaptcha-response': 'dummy_captcha'
        }

        with self.client:  # Use Flask test client
            response = self.client.post(url_for('absences.record_absence'), data=form_data, follow_redirects=False)

        # Ensure the absence was added to the database
        mock_db_add.assert_called_once()
        mock_db_commit.assert_called_once()
        mock_send_email.assert_called_once()

        # Ensure successful redirection
        self.assertEqual(response.status_code, 302)  # Expect redirect
        self.assertIn("/thank_you", response.location)  # ✅ Check the redirect URL

if __name__ == '__main__':
    unittest.main()