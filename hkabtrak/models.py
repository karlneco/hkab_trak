from hkabtrak import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Class(db.Model):
    __tablename__ = 'class'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    teacher = db.relationship('Teacher', backref='class', lazy='dynamic')

    def __repr__(self):
        return f'<Class {self.name}>'


class Absence(db.Model):
    __tablename__ = 'absence'
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(64), index=True)
    reason = db.Column(db.String(256))
    date = db.Column(db.Date)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))

    def __repr__(self):
        return f'<Absence {self.student_name} {self.date}>'


class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), db.ForeignKey('user.email'))
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))

    # user = db.relationship('User', foreign_keys=[email], back_populates='teacher')
    def __repr__(self):
        return f'<Teacher {self.username}>'


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    user_type = db.Column(db.String(1), default="N")
    # teacher = db.relationship('Teacher', foreign_keys=[email], back_populates='user')

    def __init__(self, email, password, user_type):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.user_type = user_type

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return self.email
