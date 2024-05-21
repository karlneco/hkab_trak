from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from hkabtrak.models import Absence, Class, load_user, User, Semester
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from hkabtrak import db, absences

absences_bp = Blueprint('absences', __name__, template_folder='templates')

valid_reasons = ['Absent', 'Late', 'Leaving Early', 'Absent for a Time', '欠席', '遅刻', '早退', '時間で欠席']


@absences_bp.route('/record_absence', methods=['GET', 'POST'])
def record_absence():
    if request.method == 'POST':
        parent_email = request.form['parent_email']
        class_id = request.form['class_id']
        student_name = request.form['student_name']
        reason = request.form['reason']
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        comment = request.form['comment']

        date_str = request.form.get('date')
        try:
            absence_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time() if start_time_str else None
            end_time = datetime.strptime(end_time_str, '%H:%M').time() if end_time_str else None
            print("Parsed date:", absence_date)  # Debugging line
        except ValueError:
            flash('Invalid date and/or time format.', 'error')
            return redirect(url_for('record_absence'))

        # Validate date is not in the past
        # today = date.today()
        # if absence_date < today:
        #     flash('The date cannot be in the past.', 'error')
        #     return redirect(url_for('record_absence'))

        # Validate email format (simple check)
        if '@' not in parent_email or '.' not in parent_email.split('@')[-1]:
            flash('Invalid email format.', 'error')
            return redirect(url_for('record_absence'))

        # Validate reason
        if reason not in valid_reasons:
            flash('Invalid reason for absence.', 'error')
            return redirect(url_for('record_absence'))

        # Additional validation based on reason
        if reason == "Late" and not start_time:
            flash('Expected time is required for "Late".', 'error')
            return redirect(url_for('record_absence'))
        if reason == "Leaving Early" and not end_time:
            flash('Leaving time is required for "Leaving Early".', 'error')
            return redirect(url_for('record_absence'))
        if reason == "Absent for a Time" and (not start_time or not end_time):
            flash('Both leaving and return times are required for "Absent for a Time".', 'error')
            return redirect(url_for('record_absence'))

        absence = Absence(student_name=student_name, reason=reason, class_id=class_id, date=absence_date,
                          start_time=start_time, end_time=end_time, parent_email=parent_email, comment=comment)
        db.session.add(absence)
        db.session.commit()

        return redirect(url_for('absences.thank_you'))

    classes = Class.query.all()
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('new_absence.html', classes=classes, today=today)


@absences_bp.route('/thank_you')
def thank_you():
    return render_template('absence_submited.html')


@absences_bp.route('/list', methods=['GET', 'POST'])
@login_required
def list():
    user = load_user(current_user.get_id())
    if not user:
        return redirect(url_for('login'))

    classes = user.classes
    all_absences = []
    for class_obj in classes:
        absences = Absence.query.filter_by(class_id=class_obj.id).all()
        all_absences.extend(absences)

    all_absences_sorted = sorted(all_absences, key=lambda x: x.date, reverse=True)
    this_saturday = date.today() + timedelta((5 - date.today().weekday()) % 7)

    return render_template('list.html', absences=all_absences_sorted, classes=classes, this_saturday=this_saturday)


@absences_bp.route('/students')
@login_required
def students():
    today = date.today()

    # Fetch all classes where the teacher is involved
    classes = Class.query.join(Class.staff).filter(User.id == current_user.id).all()

    semesters = Semester.query.order_by(Semester.start_date.desc()).all()  # Order by start date descending
    selected_semester_id = request.args.get('semester_id', type=int)

    if selected_semester_id:
        selected_semester = Semester.query.get(selected_semester_id)
    else:
        # Default to the current semester
        for semester in semesters:
            if semester.start_date <= today <= semester.end_date:
                selected_semester = semester
                break
        # If no current semester, default to the most recent one
        if not selected_semester and semesters:
            selected_semester = semesters[0]

    class_absences_summary = {}
    if selected_semester:
        for cls in classes:
            student_hours = {}
            for absence in cls.absences:
                if selected_semester.start_date <= absence.date <= selected_semester.end_date:
                    duration = calculate_absence_duration(cls, absence)
                    if absence.student_name in student_hours:
                        student_hours[absence.student_name] += duration
                    else:
                        student_hours[absence.student_name] = duration

            if student_hours:
                class_absences_summary[(cls.name, cls.id)] = student_hours

    return render_template('by_student.html', class_absences=class_absences_summary, semesters=semesters,
                           selected_semester=selected_semester)


@absences_bp.route('/student/<int:grade>/<student_name>/', methods=['GET', 'POST'])
def student_absences(grade, student_name):
    semesters = Semester.query.order_by(Semester.start_date.desc()).all()
    selected_semester_id = request.args.get('semester_id', type=int)

    if selected_semester_id is None or selected_semester_id == -1:  # -1 for 'All Time'
        absences = Absence.query.join(Absence.course).filter(Absence.student_name == student_name,
                                                             Class.id == grade).all()
        selected_semester = None
    else:
        selected_semester = Semester.query.get(selected_semester_id)
        absences = Absence.query.join(Absence.course).filter(
            Absence.student_name == student_name,
            Absence.date.between(selected_semester.start_date, selected_semester.end_date),
            Class.id == grade
        ).all()

    for absence in absences:
        duration = calculate_absence_duration(absence.course, absence)
        setattr(absence, 'duration', duration)

    return render_template('single_student.html', absences=absences, semesters=semesters,
                           selected_semester=selected_semester, student_name=student_name, grade=grade)

def calculate_absence_duration(cls, absence):
    # Start and end times of the class and lunch
    class_start = datetime.combine(absence.date, cls.day_start)
    class_end = datetime.combine(absence.date, cls.day_end)
    lunch_start = datetime.combine(absence.date, cls.lunch_start)
    lunch_end = datetime.combine(absence.date, cls.lunch_end)

    match absence.reason:
        case 'Absent':
            absence_start = class_start
            absence_end = class_end
        case 'Late':
            absence_start = class_start
            absence_end = datetime.combine(absence.date, absence.start_time)
        case 'Leaving Early':
            absence_start = datetime.combine(absence.date, absence.end_time)
            absence_end = class_end
        case 'Absent for a Time':
            absence_start = datetime.combine(absence.date, absence.start_time)
            absence_end = datetime.combine(absence.date, absence.end_time)

    # Adjust absence start and end times to be within the class hours
    absence_start = max(absence_start, class_start)
    absence_end = min(absence_end, class_end)

    # Calculate total duration excluding lunch
    if absence_end <= lunch_start:
        # Absence ends before lunch starts
        duration = absence_end - absence_start
    elif absence_start >= lunch_end:
        # Absence starts after lunch ends
        duration = absence_end - absence_start
    else:
        # Absence spans over the lunch period
        pre_lunch = max(timedelta(0), lunch_start - absence_start)
        post_lunch = max(timedelta(0), absence_end - lunch_end)
        duration = pre_lunch + post_lunch

    return duration.total_seconds() / 3600  # Convert duration to hours

