from sqlalchemy import func

from hkabtrak import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def load_course(class_id):
    return Class.query.get(class_id)


staff_class = db.Table(
    "staff_class",
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('class_id', db.Integer, db.ForeignKey('class.id')),
)

class Class(db.Model):
    __tablename__ = 'class'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    instructions = db.Column(db.String(512), nullable=True)
    day_start = db.Column(db.Time, nullable=True)
    lunch_start = db.Column(db.Time, nullable=True)
    lunch_end = db.Column(db.Time, nullable=True)
    day_end = db.Column(db.Time, nullable=True)
    staff = db.relationship('User', secondary=staff_class, back_populates='classes')
    absences = db.relationship('Absence', back_populates='course')

    def __repr__(self):
        return f'<Class {self.name}>'


class Absence(db.Model):
    __tablename__ = 'absence'
    id = db.Column(db.Integer, primary_key=True)
    parent_email = db.Column(db.String(128))
    student_name = db.Column(db.String(64), index=True)
    reason = db.Column(db.String(256))
    absence_type = db.Column(db.String(256))
    date = db.Column(db.Date)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    comment = db.Column(db.String(512), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    course = db.relationship('Class', back_populates='absences')
    created_at = db.Column(db.DateTime, default=func.now())  # New field for creation timestamp

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
    classes = db.relationship('Class', secondary=staff_class, back_populates='staff')

    def __init__(self, email, password, name, user_type):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.user_type = user_type

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return self.email


class Semester(db.Model):
    __tablename__ = 'semesters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<Semester {self.name} from {self.start_date} to {self.end_date}>'
