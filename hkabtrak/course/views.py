from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from mongoengine import NotUniqueError
from sqlalchemy.exc import IntegrityError

from hkabtrak import db
from hkabtrak.models import Class, load_course, User

courses_bp = Blueprint('course', __name__, template_folder='templates')


def parse_time(time_str):
    default_date = "2000-01-01"  # Arbitrary fixed date
    return datetime.strptime(f"{default_date} {time_str}", '%Y-%m-%d %H:%M') if time_str else None


@courses_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        instructions = request.form['instructions']
        day_start = parse_time(request.form['day_start'])
        lunch_start = parse_time(request.form['lunch_start'])
        lunch_end = parse_time(request.form['lunch_end'])
        day_end = parse_time(request.form['day_end'])

        try:
            class_obj = Class(
                name=name, instructions=instructions,
                day_start=day_start, lunch_start=lunch_start,
                lunch_end=lunch_end, day_end=day_end
            )
            class_obj.save()

            return redirect(url_for('admin.course_list'))
        except NotUniqueError:
            flash('A class with that name already exists. Please use a different name.', 'danger')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('course_create.html')



@courses_bp.route('/edit/<string:course_name>', methods=['GET', 'POST'])
@login_required
def edit(course_name):
    course = Class.objects(name=course_name).first()
    if not course:
        # Handle the case where the course does not exist
        return "Course not found", 404

    # Fetching teacher and assistant names
    if course.teachers:
        teachers = User.objects(id__in=course.teachers)
    else:
        teachers = []

    if course.assistants:
        assistants = User.objects(id__in=course.assistants)
    else:
        assistants = []

    if request.method == 'POST':
        # Update fields
        course.name = request.form['name']
        course.instructions = request.form['instructions']
        course.day_start = parse_time(request.form['day_start'])
        course.lunch_start = parse_time(request.form['lunch_start'])
        course.lunch_end = parse_time(request.form['lunch_end'])
        course.day_end = parse_time(request.form['day_end'])

        # Save changes
        course.save()
        return redirect(url_for('admin.course_list'))

    return render_template('course_edit.html', course=course, teachers=teachers, assistants=assistants)


@courses_bp.route('/duplicate/<string:course_id>', methods=['POST'])
@login_required
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


@courses_bp.route('/delete/<string:course_id>', methods=['GET'])
@login_required
def delete(course_id):
    course = Class.objects.get(pk=course_id)
    course.delete()
    flash('Course deleted successfully.')
    return redirect(url_for('course.course_list'))


@courses_bp.route('/course_view', methods=['GET', 'POST'])
@login_required
def course_view():
    course = load_course()
    return render_template('course_edit.html', course=course)


@courses_bp.route('/course_list')
@login_required
def course_list():
    classes = Class.objects.all()
    return render_template(url_for('admin.course_list'))
