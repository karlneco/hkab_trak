from hkabtrak import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True)
    list_entry = db.Column(db.Text)
    grade_email = db.Column(db.Text)
    notes = db.Column(db.Text)

    def __int__(self, list_entry, grade_email):
        self.list_entry = list_entry
        self.grade_email = grade_email

    def __repr__(self):
        return f'{self.list_entry} will email to {self.grade_email}'


class Absence(db.Model):
    __tablename__ = 'absence'
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.Text)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))


    def __init__(self,email,password):
        self.email = email
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return self.email
