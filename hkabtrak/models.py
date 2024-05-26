from hkabtrak import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def load_user(email):
    return User.objects(email=email).get_or_404()


def load_course(name):
    return Class.objects(name=name).get_or_404()


USER_TYPES = (
    ('A', 'Administrator'),
    ('T', 'Teacher'),
    ('H', 'Teacher Assistant'),
    ('N', 'Not Assigned')
)

ABSENCE_TYPES = (
    ('A', 'Absent'),
    ('L', 'Late'),
    ('E', 'Leave Early'),
    ('T', 'Absent for a time')
)


class Class(db.Document):
    name = db.StringField(required=True, unique=True)
    instructions = db.StringField()
    day_start = db.DateTimeField()
    lunch_start = db.DateTimeField()
    lunch_end = db.DateTimeField()
    day_end = db.DateTimeField()
    # Direct reference to User document IDs
    teachers = db.ListField(db.ObjectIdField())
    assistants = db.ListField(db.ObjectIdField())

    def __repr__(self):
        return f'<Class {self.name}>'


class Absence(db.Document):
    parent_email = db.StringField(required=True)
    student_name = db.StringField(required=True)
    reason = db.StringField()
    type = db.StringField(required=True, choices=ABSENCE_TYPES)  # Updated to use choices
    date = db.DateTimeField(required=True)
    start_time = db.DateTimeField()
    end_time = db.DateTimeField()
    comment = db.StringField()
    # Storing reference to Class
    class_id = db.ObjectIdField(required=True)

    meta = {
        'indexes': [
            # Indexing by date and type can be useful for quickly finding absences by when they occurred and what type they are.
            {'fields': ['date', 'type']},
            # Additional index if querying often by class_id might be sensible.
            {'fields': ['class_id']}
        ]
    }

    def __repr__(self):
        return f'<Absence {self.student_name} {self.date} {self.type}>'


class User(db.Document, UserMixin):
    email = db.StringField(required=True, unique=True)
    name = db.StringField()
    password_hash = db.StringField()
    is_active = db.BooleanField(default=True)
    user_type = db.StringField(default='N', choices=USER_TYPES)
    # In MongoDB, you can store related object IDs directly or embed documents
    classes = db.ListField(db.ObjectIdField())
    meta = {
        'indexes': [
            {'fields': ['email'], 'unique': True}
        ]
    }

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return self.email


class Semester(db.Document):
    name = db.StringField(required=True)
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()

    def __repr__(self):
        return f'<Semester {self.name} from {self.start_date} to {self.end_date}>'
