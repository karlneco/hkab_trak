from hkabtrak import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

teacher_class = db.Table(
    "teacher_class",
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('class_id', db.Integer, db.ForeignKey('class.id')),
)


class Class(db.Model):
    __tablename__ = 'class'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    teachers = db.relationship('User', secondary=teacher_class, back_populates='classes')

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


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    user_type = db.Column(db.String(1), default="N")
    classes = db.relationship('Class', secondary=teacher_class, back_populates='teachers')

    def __init__(self, email, password, name, user_type):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.user_type = user_type

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return self.email
