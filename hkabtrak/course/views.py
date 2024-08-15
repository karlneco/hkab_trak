from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from hkabtrak import db
from hkabtrak.models import Class, load_course
from hkabtrak.util import admin_required

courses_bp = Blueprint('course', __name__, template_folder='templates')


@courses_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        instructions = request.form['instructions']
        day_start_str = request.form['day_start']
        lunch_start_str = request.form['lunch_start']
        lunch_end_str = request.form['lunch_end']
        day_end_str = request.form['day_end']
        day_start = datetime.strptime(day_start_str, '%H:%M').time() if day_start_str else None
        lunch_start = datetime.strptime(lunch_start_str, '%H:%M').time() if lunch_start_str else None
        lunch_end = datetime.strptime(lunch_end_str, '%H:%M').time() if lunch_end_str else None
        day_end = datetime.strptime(day_end_str, '%H:%M').time() if day_end_str else None

        try:
            class_obj = Class(
                name=name, instructions=instructions,
                day_start=day_start, lunch_start=lunch_start,
                lunch_end=lunch_end, day_end=day_end
            )
            db.session.add(class_obj)
            db.session.commit()
            return redirect(url_for('admin.course_list'))
        except IntegrityError:
            db.session.rollback()  # Roll back the transaction so you can continue using the session
            flash('A class with that name already exists. Please use a different name.', 'danger')
            return render_template('course_create.html', name=name, instructions=instructions,
                                   day_start=day_start, lunch_start=lunch_start,
                                   lunch_end=lunch_end, day_end=day_end)
    return render_template('course_create.html')


@courses_bp.route('/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(course_id):
    course = Class.query.get_or_404(course_id)
    # Filter staff into teachers and assistants
    teachers = [user for user in course.staff if user.user_type == 'T']
    assistants = [user for user in course.staff if user.user_type == 'H']

    if request.method == 'POST':
        # Since no editing of teachers or assistants, only handle other fields
        course.name = request.form['name']
        course.instructions = request.form['instructions']
        day_start_str = request.form['day_start']
        lunch_start_str = request.form['lunch_start']
        lunch_end_str = request.form['lunch_end']
        day_end_str = request.form['day_end']
        course.day_start = datetime.strptime(day_start_str, '%H:%M').time() if day_start_str else None
        course.lunch_start = datetime.strptime(lunch_start_str, '%H:%M').time() if lunch_start_str else None
        course.lunch_end = datetime.strptime(lunch_end_str, '%H:%M').time() if lunch_end_str else None
        course.day_end = datetime.strptime(day_end_str, '%H:%M').time() if day_end_str else None
        db.session.commit()

        if request.form['action'] == 'duplicate':
            # Duplicate logic
            new_course = Class(name="Copy of " + course.name, instructions=course.instructions, day_start=course.day_start,
                               lunch_start=course.lunch_start, day_end=course.day_end, lunch_end=course.lunch_end)
            db.session.add(new_course)
            db.session.commit()
            return redirect(url_for('course.edit', course_id=new_course.id))

        return redirect(url_for('admin.course_list'))

    return render_template('course_edit.html', course=course, teachers=teachers, assistants=assistants)


@courses_bp.route('/duplicate/<int:course_id>', methods=['POST'])
@login_required
@admin_required
def duplicate(course_id):
    original_course = Class.query.get_or_404(course_id)
    new_course = Class(
        name="Copy of " + original_course.name,
        instructions=original_course.instructions,
        day_start=original_course.day_start,
        lunch_start=original_course.lunch_start,
        lunch_end=original_course.lunch_end,
        day_end=original_course.day_end,
        # Ensure any other fields are copied as necessary
    )
    db.session.add(new_course)
    db.session.commit()
    flash('Course duplicated successfully. Please edit the name.')
    return redirect(url_for('course.edit', course_id=new_course.id))


@courses_bp.route('/delete/<int:course_id>', methods=['GET'])
@login_required
@admin_required
def delete(course_id):
    course = Class.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully.')
    return redirect(url_for('course.course_list'))


@courses_bp.route('/course_view', methods=['GET', 'POST'])
@login_required
@admin_required
def course_view():
    course = load_course()
    return render_template('course_edit.html', course=course)


@courses_bp.route('/course_list')
@login_required
@admin_required
def course_list():
    classes = Class.query.all()
    return render_template(url_for('admin.course_list'))
