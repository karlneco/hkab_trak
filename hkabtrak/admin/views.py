from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from hkabtrak.models import Class, load_user, User
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from hkabtrak import db
from sqlalchemy.orm import joinedload

admin_bp = Blueprint('admin', __name__, template_folder='templates')


@admin_bp.route('/admin')
@admin_bp.route('/main', methods=['GET'])
@login_required
def admin_main():
    return render_template('home.html')


@admin_bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect('/')


@admin_bp.route('/staff')
@login_required
def staff_list():
    staff = User.query.all()
    return render_template('staff_list.html', staff=staff)


@admin_bp.route('/staff/edit/<int:staff_id>', methods=['GET', 'POST'])
@login_required
def staff_edit(staff_id):
    # Load the teacher data from the database based on user_id
    staff = User.query.get(staff_id)

    staff_classes = [{'id': c.id, 'name': c.name} for c in staff.classes]

    classes = Class.query.all()
    all_classes = [{'id': c.id, 'name': c.name} for c in classes]

    if request.method == 'POST':
        # Update teacher data based on form input
        staff.name = request.form['name']
        staff.email = request.form['email']
        staff.is_active = 'is_active' in request.form
        staff.user_type = request.form['user_type']

        # Commit changes to the database
        db.session.commit()

        # Redirect to the teacher list or another page
        return redirect(url_for('admin.staff_list'))

    return render_template('staff_edit.html', staff=staff, classes=staff_classes, all_classes=all_classes)


@admin_bp.route('/courses')
@login_required
def course_list():
    courses = Class.query.all()
    return render_template('courses.html', courses=courses)


@admin_bp.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
def course_edit(course_id):
    course = Class.query.get_or_404(course_id)
    # Filter staff into teachers and assistants
    teachers = [user for user in course.staff if user.user_type == 'T']
    assistants = [user for user in course.staff if user.user_type == 'H']

    if request.method == 'POST':
        # Since no editing of teachers or assistants, only handle other fields
        course.name = request.form['name']
        course.instructions = request.form['instructions']
        db.session.commit()
        return redirect(url_for('admin.course_list'))

    return render_template('course_edit.html', course=course, teachers=teachers, assistants=assistants)


@admin_bp.route('/admin/reset_password/<int:staff_id>', methods=['POST'])
@login_required
def reset_password(staff_id):
    if request.method == 'POST':
        new_password = request.form['new_password']

        # Retrieve the teacher from the database
        staff = User.query.get(staff_id)

        if staff is not None:
            # Set the new password for the teacher
            staff.password_hash = generate_password_hash(
                new_password)  # Ensure you have the correct password hashing function

            # Commit changes to the database
            db.session.commit()

            flash('Password reset successful', 'success')
        else:
            flash('Staff member not found', 'error')

        return redirect(url_for('admin.staff_edit', staff_id=staff_id))


# Route to get the classes for a specific teacher
@admin_bp.route('/api/staff_classes/<int:staff_id>', methods=['GET'])
@login_required
def get_staff_classes(staff_id):
    staff = User.query.get(staff_id)
    if staff:
        classes = [{'id': c.id, 'name': c.name} for c in staff.classes]
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

@admin_bp.route('/api/add_class/<int:class_id>/<int:staff_id>', methods=['POST'])
@login_required
def add_class(class_id, staff_id):
    staff = User.query.get(staff_id)
    class_to_add = Class.query.get(class_id)

    if staff and class_to_add:
        staff.classes.append(class_to_add)
        db.session.commit()
        return jsonify({'message': 'Class added successfully'})
    else:
        return jsonify({'error': 'Teacher or class not found'})

# Route to remove a class from a teacher
@admin_bp.route('/api/remove_class/<int:class_id>/<int:staff_id>', methods=['POST'])
@login_required
def remove_class(class_id, staff_id):
    staff = User.query.get(staff_id)
    class_to_remove = Class.query.get(class_id)

    if staff and class_to_remove:
        staff.classes.remove(class_to_remove)
        db.session.commit()
        return jsonify({'message': 'Class removed successfully'})
    else:
        return jsonify({'error': 'Teacher or class not found'})