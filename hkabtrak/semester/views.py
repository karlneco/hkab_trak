import random
from datetime import timedelta, datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from hkabtrak import db
from hkabtrak.models import Class, Absence, Semester

semester_bp = Blueprint('semester', __name__, template_folder='templates')


@semester_bp.route('/list', methods=['GET'])
@login_required
def semester_list():
    semesters = Semester.query.order_by(Semester.start_date.asc()).all()
    return render_template('semester_list.html', semesters=semesters)


@semester_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date and/or time format.', 'danger')
            return redirect(url_for('semester.create'))

        try:
            # Create a new Semester instance
            new_semester = Semester(name=name, start_date=start_date, end_date=end_date)
            db.session.add(new_semester)
            db.session.commit()

            flash('Semester created successfully!', 'success')
            return redirect(url_for('semester.semester_list'))
        except IntegrityError:
            db.session.rollback()  # Roll back the transaction so you can continue using the session
            flash('A semester with that name already exists. Please use a different name.', 'danger')
            return render_template('semester_create.html')

    return render_template('semester_create.html')


@semester_bp.route('/edit/<int:semester_id>', methods=['GET', 'POST'])
@login_required
def edit(semester_id):
    semester = Semester.query.get_or_404(semester_id)

    if request.method == 'POST':
        semester.name = request.form['name']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        semester.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        semester.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        db.session.commit()
        flash('Semester updated successfully!', 'success')
        return redirect(url_for('semester.semester_list'))

    return render_template('semester_edit.html', semester=semester)


@semester_bp.route('/delete/<int:semester_id>', methods=['GET', 'POST'])
@login_required
def delete(semester_id):
    semester = Semester.query.get_or_404(semester_id)
    db.session.delete(semester)
    db.session.commit()
    flash('Semester deleted successfully!', 'info')
    return redirect(url_for('semester.semester_list'))


@semester_bp.route('/delete_data/<int:semester_id>', methods=['GET'])
@login_required
def delete_data(semester_id):
    semester = Semester.query.get(semester_id)
    if not semester:
        flash('Semester not found.', 'error')
        return redirect(url_for('list_semesters'))

    # Assuming 'Absence' has a foreign key relationship with 'Semester'
    Absence.query.filter(Absence.date.between(semester.start_date, semester.end_date)).delete()
    db.session.delete(semester)
    db.session.commit()
    flash('Semester and related data deleted successfully.', 'success')
    return redirect(url_for('semester.semester_list'))


# Distributing students into classes
def distribute_students_into_classes(students, class_size=14):
    random.shuffle(students)  # Shuffle the students to randomize class assignment
    classes = [students[i:i + class_size] for i in range(0, len(students), class_size)]
    return classes


@semester_bp.route('/populate_absences/<int:semester_id>', methods=['GET'])
@login_required
def populate_absences(semester_id):
    semester = Semester.query.get(semester_id)
    if not semester:
        flash('Semester not found.', 'error')
        return redirect(url_for('list_semesters'))

    # Japanese names for random generation
    first_names = ["Haruto", "Yuto", "Souta", "Yuki", "Hayato"]
    last_names = ["Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe"]

    # Create student groups
    num_classes = 5  # Assume 5 classes for simplicity
    students_per_class = {f"Grade {i + 1}": [
        f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(9)
    ] for i in range(num_classes)}

    start_date = semester.start_date
    end_date = semester.end_date
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() == 5:  # Assuming absences are registered on Saturdays
            for class_name, students in students_per_class.items():
                class_id = Class.query.filter_by(name=class_name).first().id  # Get class id for the relationship
                for student_name in random.sample(students, k=random.randint(1, min(6, len(students)))):
                    absence_date = current_date
                    generate_and_add_absence(student_name, class_id, absence_date)
        current_date += timedelta(days=1)

    db.session.commit()
    flash('Random absences populated successfully.', 'success')
    return redirect(url_for('semester.semester_list'))


def generate_and_add_absence(student_name, class_id, absence_date):
    absence_types = ['Absent', 'Late', 'Leaving Early', 'Absent for a Time']
    reasons = ['Unwell', 'Lessons', 'Personal', 'Other']
    absence_type = random.choice(absence_types)
    reason = random.choice(reasons)

    start_time = None
    end_time = None
    if absence_type == "Late":
        start_time = datetime.strptime(f"{random.randint(9, 11)}:{random.randint(0, 59):02d}", '%H:%M').time()
    elif absence_type == "Leaving Early":
        end_time = datetime.strptime(f"{random.randint(12, 14)}:{random.randint(0, 59):02d}", '%H:%M').time()
    elif absence_type == "Absent for a Time":
        start_time = datetime.strptime(f"9:00", '%H:%M').time()
        end_time = datetime.strptime(f"12:00", '%H:%M').time()

    parent_email = f"{student_name.lower().replace(' ', '')}@example.com"

    # Creating and adding the absence record
    absence = Absence(
        parent_email=parent_email, student_name=student_name, class_id=class_id, date=absence_date,
        start_time=start_time, end_time=end_time, reason=reason, absence_type=absence_type,
        comment=generate_dynamic_comment(absence_type)
    )
    db.session.add(absence)


def generate_dynamic_comment(absence_type):
    reasons = {
        'Absent': ["体調不良", "家族の緊急事態", "家族旅行"],
        'Late': ["バスに乗り遅れ", "交通渋滞に巻き込まれ", "遅れが生じ"],
        'Leaving Early': ["医者の予約", "家族の用事", "個人的な事情"],
        'Absent for a Time': ["医療的な予約", "個人的な理由", "セラピー"]
    }
    templates = {
        'Absent': "因みに{reason}で休みます。すぐに戻る予定です。",
        'Late': "{reason}ために遅れています。ご迷惑をおかけして申し訳ございません。",
        'Leaving Early': "{reason}のため早退します。欠席した授業については後ほど対応します。",
        'Absent for a Time': "{reason}のため一時的に外出します。すぐに戻ります。"
    }

    reason = random.choice(reasons[absence_type]) if absence_type in reasons else "特別な理由"
    template = templates[absence_type] if absence_type in templates else "詳細は提供されていません。{reason}"
    return template.format(reason=reason)
