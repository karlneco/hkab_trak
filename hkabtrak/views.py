from hkabtrak import db, login_manager
from flask import render_template, request, redirect, url_for, flash, Blueprint, Flask
from flask_sqlalchemy import get_debug_queries
from flask_login import login_user, login_required, logout_user, current_user
root_bp = Blueprint('root', __name__, template_folder='templates')

@root_bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
