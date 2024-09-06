from datetime import datetime, date, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages, current_app, \
    jsonify
from flask_login import login_required, current_user
from flask_mail import Message
from wtforms.validators import DataRequired

from hkabtrak import db, mail, bcc_address
from hkabtrak.absence_form import AbsenceForm
from hkabtrak.models import Absence, Class, load_user, User, Semester, load_course
from hkabtrak.util import admin_required

absences_bp = Blueprint('absences', __name__, template_folder='templates')

valid_types = ['欠席', '遅刻', '早退', '中抜け']


@absences_bp.route('/record_absence', methods=['GET', 'POST'])
def record_absence():
    form = AbsenceForm()
    default_course_choice = [('', '学年を選択してください')]
    form.class_id.choices = default_course_choice + [
        (cls.id, cls.name, {'data-instructions': cls.instructions or 'None'}) for cls in Class.query.all()
    ]

    if request.method == 'POST':
        reason = form.reason.data
        # Add conditional validators
        if reason == '遅刻':
            form.start_time.validators.append(DataRequired(message="Expected time is required for 'Late'."))
        if reason == '早退':
            form.end_time.validators.append(DataRequired(message="Leaving time is required for 'Leaving Early'."))
        if reason == '中抜け':
            form.start_time.validators.append(DataRequired(message="Leaving time is required for 'Absent for a Time'."))
            form.end_time.validators.append(DataRequired(message="Return time is required for 'Absent for a Time'."))

        form.validate()
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')

    if current_app.config.get('RECAPTCHA_ENABLED'):
        captcha_response = request.form['g-recaptcha-response']
    else:
        captcha_response = 'testing'
    if len(captcha_response) > 0:
        parent_email = form.parent_email.data
        class_id = form.class_id.data
        grade_name = load_course(class_id).name
        student_name = form.student_name.data
        absence_type = form.absence_type.data
        reason = form.reason.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        comment = form.comment.data
        date = form.date.data

        if reason == 'その他':
            reason = 'その他' + ': ' + form.other_reason.data

        absence = Absence(
            student_name=student_name,
            reason=reason,
            class_id=class_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            parent_email=parent_email,
            absence_type=absence_type,
            comment=comment
        )
        db.session.add(absence)
        db.session.commit()

        cls = Class.query.get(class_id)
        if cls:
            staff_emails = [user.email for user in cls.staff]
            send_absence_notification(parent_email, staff_emails, student_name, grade_name, absence_type, reason, date,
                                      start_time, end_time,
                                      comment)

        get_flashed_messages(with_categories=True)
        return redirect(url_for('root.thank_you'))
    else:
        get_flashed_messages(with_categories=True)

    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('new_absence.html', form=form, today=today)


@absences_bp.route('/thank_you')
def thank_you():
    return render_template('absence_submited.html')


@absences_bp.route('/list', methods=['GET', 'POST'])
@login_required
def list():
    user = load_user(current_user.get_id())
    if not user:
        return redirect(url_for('login'))

    if user.user_type == 'A':
        classes = Class.query.all()
    else:
        classes = user.classes
    all_absences = []
    date_filter = request.args.get('filterDate')  # Get date filter from query parameters

    try:
        # Convert the date from string to datetime.date object if provided
        selected_date = datetime.strptime(date_filter, '%Y-%m-%d').date() if date_filter else None
    except TypeError:
        selected_date = None

    for class_obj in classes:
        if selected_date:
            # Filter absences by class and selected date if a date is provided
            absences = Absence.query.filter_by(class_id=class_obj.id, date=selected_date).all()
        else:
            # Get all absences if no date is provided
            absences = Absence.query.filter_by(class_id=class_obj.id).all()
        all_absences.extend(absences)

    all_absences_sorted = sorted(all_absences, key=lambda x: x.date, reverse=True)
    this_saturday = date.today() + timedelta((5 - date.today().weekday()) % 7)

    return render_template('list.html', absences=all_absences_sorted, classes=classes, this_saturday=this_saturday,
                           selected_date=selected_date)


@absences_bp.route('/api/delete_absence/<int:absence_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_absence(absence_id):
    # Get the absence record
    absence = Absence.query.get(absence_id)

    if absence:
        # Delete the record
        db.session.delete(absence)
        db.session.commit()
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Absence not found"}), 404


@absences_bp.route('/students')
@login_required
def students():
    today = date.today()
    user = load_user(current_user.get_id())

    # Fetch all classes where the teacher is involved
    if user.user_type == 'A':
        classes = Class.query.all()
    else:
        classes = Class.query.join(Class.staff).filter(User.id == current_user.id).all()

    semesters = Semester.query.order_by(Semester.start_date.asc()).all()  # Order by start date descending
    selected_semester_id = request.args.get('semester_id', type=int)

    selected_semester = None

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
            student_absences = {}
            for absence in cls.absences:
                if selected_semester.start_date <= absence.date <= selected_semester.end_date:
                    if absence.student_name not in student_absences:
                        student_absences[absence.student_name] = {'days': 0, 'hours': 0}

                    if absence.absence_type == 'Absent':
                        if absence.student_name in student_absences:
                            student_absences[absence.student_name]['days'] += 1
                    else:
                        duration = calculate_absence_duration(cls, absence)
                        if absence.student_name in student_absences:
                            student_absences[absence.student_name]['hours'] += duration

            if student_absences:
                class_absences_summary[(cls.name, cls.id)] = student_absences

    return render_template('by_student.html', class_absences=class_absences_summary, semesters=semesters,
                           selected_semester=selected_semester)


@absences_bp.route('/student/<int:grade>/<student_name>/', methods=['GET', 'POST'])
def student_absences(grade, student_name):
    semesters = Semester.query.order_by(Semester.start_date.asc()).all()
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

    days_missed = 0
    for absence in absences:
        if absence.absence_type != 'Absent':
            duration = calculate_absence_duration(absence.course, absence)
            setattr(absence, 'duration', duration)
        else:
            days_missed += 1

    return render_template('single_student.html', absences=absences, semesters=semesters,
                           selected_semester=selected_semester, student_name=student_name, grade=grade,
                           days_missed=days_missed)


def calculate_absence_duration(cls, absence):
    # Start and end times of the class and lunch
    class_start = datetime.combine(absence.date, cls.day_start)
    class_end = datetime.combine(absence.date, cls.day_end)
    lunch_start = datetime.combine(absence.date, cls.lunch_start)
    lunch_end = datetime.combine(absence.date, cls.lunch_end)

    match absence.absence_type:
        case '欠席':  # Absent
            absence_start = class_start
            absence_end = class_end
        case '遅刻':  # Late
            absence_start = class_start
            absence_end = datetime.combine(absence.date, absence.start_time)
        case '早退':  # Leaving Early
            absence_start = datetime.combine(absence.date, absence.end_time)
            absence_end = class_end
        case '中抜け':  # Absent for a time
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


def send_absence_notification(parent_email, recipients, student_name, grade, absence_type, reason, absence_date,
                              start_time, end_time,
                              comment):
    """
    Send email notifications to the specified recipients about the student's absence.
    """
    subject = grade + student_name + "さんの欠席欠課連絡受領のお知らせ_" + absence_date.strftime('%Y-%m-%d')
    body = render_template(
        'absence_notification.html',
        student_name=student_name,
        grade=grade,
        reason=reason,
        absence_type=absence_type,
        date=absence_date,
        start_time=start_time,
        end_time=end_time,
        comment=comment
    )
    cc_ = [current_app.config['MAIL_CC']]
    recipients.append(parent_email)
    msg = Message(subject, recipients=recipients, cc=cc_, html=body)
    msg.sender = ('カルガリー補習授業校', current_app.config['MAIL_DEFAULT_SENDER'])
    mail.send(msg)
