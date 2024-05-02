from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from hkabtrak.models import Class, load_user, User
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from hkabtrak import db
from sqlalchemy.orm import joinedload

admin_bp = Blueprint('admin', __name__, template_folder='templates')


@admin_bp.route('/admin')
@admin_bp.route('/main', methods=['GET'])
def admin_main():
    return render_template('home.html')


@admin_bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return render_template('index.html')


@admin_bp.route('/teachers')
@login_required
def teacher_list():
    teachers = User.query.all()
    return render_template('teachers.html', teachers=teachers)


@admin_bp.route('/teachers/edit/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def teacher_edit(teacher_id):
    # Load the teacher data from the database based on teacher_id
    teacher = User.query.get(teacher_id)

    teacher_classes = [{'id': c.id, 'name': c.name} for c in teacher.classes]

    classes = Class.query.all()
    all_classes = [{'id': c.id, 'name': c.name} for c in classes]

    if request.method == 'POST':
        # Update teacher data based on form input
        teacher.name = request.form['name']
        teacher.email = request.form['email']
        teacher.is_active = 'is_active' in request.form
        teacher.user_type = request.form['user_type']

        # Commit changes to the database
        db.session.commit()

        # Redirect to the teacher list or another page
        return redirect(url_for('admin.teacher_list'))

    return render_template('teacher_edit.html', teacher=teacher, classes=teacher_classes, all_classes=all_classes)


@admin_bp.route('/courses')
@login_required
def course_list():
    courses = Class.query.all()
    return render_template('courses.html', courses=courses)


@admin_bp.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
def course_edit(course_id):
    # Load the teacher data from the database based on teacher_id
    course = Class.query.get(course_id)

    if request.method == 'POST':
        # Update teacher data based on form input
        course.name = request.form['name']

        # Commit changes to the database
        db.session.commit()

        # Redirect to the teacher list or another page
        return redirect(url_for('admin.course_list'))

    return render_template('course_edit.html', course=course)


@admin_bp.route('/admin/reset_password/<int:teacher_id>', methods=['POST'])
@login_required
def reset_password(teacher_id):
    if request.method == 'POST':
        new_password = request.form['new_password']

        # Retrieve the teacher from the database
        teacher = User.query.get(teacher_id)

        if teacher is not None:
            # Set the new password for the teacher
            teacher.password_hash = generate_password_hash(
                new_password)  # Ensure you have the correct password hashing function

            # Commit changes to the database
            db.session.commit()

            flash('Password reset successful', 'success')
        else:
            flash('Teacher not found', 'error')

        return redirect(url_for('admin.teacher_edit', teacher_id=teacher_id))


# Route to get the classes for a specific teacher
@admin_bp.route('/api/teacher_classes/<int:teacher_id>', methods=['GET'])
@login_required
def get_teacher_classes(teacher_id):
    teacher = User.query.get(teacher_id)
    if teacher:
        classes = [{'id': c.id, 'name': c.name} for c in teacher.classes]
        return jsonify({'classes': classes})
    else:
        return jsonify({'classes': []})


# Route to get all available classes
@admin_bp.route('/api/all_classes', methods=['GET'])
@login_required
def get_all_classes():
    classes = Class.query.all()
    all_classes = [{'id': c.id, 'name': c.name} for c in classes]
    return jsonify({'classes': all_classes})

@admin_bp.route('/api/add_class/<int:class_id>/<int:teacher_id>', methods=['POST'])
@login_required
def add_class(class_id, teacher_id):
    teacher = User.query.get(teacher_id)
    class_to_add = Class.query.get(class_id)

    if teacher and class_to_add:
        teacher.classes.append(class_to_add)
        db.session.commit()
        return jsonify({'message': 'Class added successfully'})
    else:
        return jsonify({'error': 'Teacher or class not found'})

# Route to remove a class from a teacher
@admin_bp.route('/api/remove_class/<int:class_id>/<int:teacher_id>', methods=['POST'])
@login_required
def remove_class(class_id, teacher_id):
    teacher = User.query.get(teacher_id)
    class_to_remove = Class.query.get(class_id)

    if teacher and class_to_remove:
        teacher.classes.remove(class_to_remove)
        db.session.commit()
        return jsonify({'message': 'Class removed successfully'})
    else:
        return jsonify({'error': 'Teacher or class not found'})