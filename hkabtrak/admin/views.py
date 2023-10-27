from flask import Blueprint, render_template, request, redirect, url_for, flash
from hkabtrak.models import Teacher, Class, load_user, User
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from hkabtrak import db

admin_bp = Blueprint('admin', __name__, template_folder='templates')


@admin_bp.route('/admin')
@admin_bp.route('/main', methods=['GET'])
def admin_main():
    return render_template('home.html')


@admin_bp.route('/teachers')
def teacher_list():
    teachers = Teacher.query.all()
    return render_template('teachers.html', teachers=teachers)
