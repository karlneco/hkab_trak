from datetime import time, date
from unittest import TestCase

from hkabtrak.absences.views import calculate_absence_duration
from hkabtrak.models import Class, Absence


class TestAbsences(TestCase):

    def setUp(self):
        # Setup a dummy class for testing
        self.test_class = Class(
            day_start=time(9, 0),
            day_end=time(15, 0),
            lunch_start=time(12, 0),
            lunch_end=time(13, 0)
        )

        # Setup a test date
        self.test_date = date.today()

    def test_full_day_absence(self):
        # Student absent for the whole day
        absence = Absence(
            date=self.test_date,
            absence_type='Absent'
        )
        duration = calculate_absence_duration(self.test_class, absence)
        self.assertEqual(duration, 5)  # missed 5 hours (excluding lunch)

    def test_late_arrival(self):
        # Student arrives late, missing lunch
        absence = Absence(
            date=self.test_date,
            start_time=time(10, 0),
            absence_type='Late',
        )
        duration = calculate_absence_duration(self.test_class, absence)
        self.assertEqual(duration, 1)  # Missed 1 hour - from 9:00am to 10:00am

    def test_leaving_early(self):
        # Student leaves early, after lunch
        absence = Absence(
            date=self.test_date,
            end_time=time(14, 0),
            absence_type='Leaving Early'
        )
        duration = calculate_absence_duration(self.test_class, absence)
        self.assertEqual(duration, 1)  # Missed 1 hour; from 2:00pm to 3:00pm

    def test_absent_for_a_time_before_lunch(self):
        # Student leaves early, after lunch
        absence = Absence(
            date=self.test_date,
            start_time=time(10, 0),
            end_time=time(11, 0),
            absence_type='Absent for a Time'
        )
        duration = calculate_absence_duration(self.test_class, absence)
        self.assertEqual(duration, 1)  # missed 1 hour; from 10:00am to 11:00am

    def test_absent_for_a_time_after_before_lunch(self):
        # Student leaves early, after lunch
        absence = Absence(
            date=self.test_date,
            start_time=time(13, 30),
            end_time=time(14, 30),
            absence_type='Absent for a Time'
        )
        duration = calculate_absence_duration(self.test_class, absence)
        self.assertEqual(duration, 1)  # missed 1 hour; from 1:30pm to 2:30pm

    def test_absent_for_a_time_including_whole_lunch(self):
        # Student leaves early, after lunch
        absence = Absence(
            date=self.test_date,
            start_time=time(10, 30),
            end_time=time(14, 30),
            absence_type='Absent for a Time'
        )
        duration = calculate_absence_duration(self.test_class, absence)
        self.assertEqual(duration, 3)  # missed 3 hour; from 10:00am to 12:00pm and 1:00pm to 2:00pm

    def test_absent_for_a_time_before_lunch_and_first_half_of_lunch(self):
        # Student leaves early, after lunch
        absence = Absence(
            date=self.test_date,
            start_time=time(11, 0),
            end_time=time(12, 30),
            absence_type='Absent for a Time'
        )
        duration = calculate_absence_duration(self.test_class, absence)
        self.assertEqual(duration, 1)  # missed 1 hour; from 11:00pm to 12:30pm


    def test_absent_for_a_time_after_lunch_and_last_half_of_lunch(self):
        # Student leaves early, after lunch
        absence = Absence(
            date=self.test_date,
            start_time=time(12, 30),
            end_time=time(14, 0),
            absence_type='Absent for a Time'
        )
        duration = calculate_absence_duration(self.test_class, absence)
        self.assertEqual(duration, 1)  # missed 1 hour; from 11:00pm to 12:30pm

if __name__ == '__main__':
    TestCase.main()
