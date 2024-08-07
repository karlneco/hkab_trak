from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SelectField, DateField, TimeField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Email

class AbsenceForm(FlaskForm):
    parent_email = StringField('Parent\'s Email', validators=[DataRequired(), Email()])
    class_id = SelectField('Class', validators=[DataRequired()])
    student_name = StringField('Student Name', validators=[DataRequired()])
    reason = RadioField('Reason for Absence', choices=[
        ('Unwell', 'Unwell'),
        ('Lessons', 'Lessons'),
        ('Personal', 'Personal'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    other_reason = StringField('Please specify', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('Start Time')
    end_time = TimeField('End Time')
    comment = TextAreaField('Comment', validators=[DataRequired()])
    recaptcha = RecaptchaField()
