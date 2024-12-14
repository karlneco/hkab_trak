import os

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SelectField, DateField, TimeField, TextAreaField, RadioField, validators
from wtforms.validators import DataRequired, Email


class CustomSelectField(SelectField):
    def __init__(self, label=None, validators=None, coerce=str, option_kwargs=None, **kwargs):
        super().__init__(label, validators, coerce=coerce, **kwargs)
        self.option_kwargs = option_kwargs or {}

    def iter_choices(self):
        for value, label, kwargs in self.choices:
            yield (value, label, self.coerce(value), self.option_kwargs.get(value, {}))


class AbsenceForm(FlaskForm):
    parent_email = StringField('Email', validators=[DataRequired(), Email()])
    class_id = SelectField('Class', validators=[DataRequired()])
    student_name = StringField('Student Name', validators=[DataRequired()])
    absence_type = SelectField('Type of Absence', choices=[
        ('Select a Type', ''),
        ('欠席', '欠席'),
        ('遅刻', '遅刻'),
        ('早退', '早退'),
        ('中抜け', '中抜け')
    ], validators=[DataRequired()])
    reason = SelectField('Reason for Absence', choices=[
        ('体調不良', '体調不良'),
        ('習い事', '習い事'),
        ('私事都合', '私事都合'),
        ('その他', 'その他')
    ], validators=[DataRequired()])
    other_reason = StringField('Please specify')
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=(validators.Optional(),))
    end_time = TimeField('End Time', validators=(validators.Optional(),))
    comment = TextAreaField('Comment', validators=[DataRequired()])
    is_production = os.getenv('FLASK_ENV') == 'production'
    if is_production:
        recaptcha = RecaptchaField()
