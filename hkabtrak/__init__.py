from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Config
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'staff.staff_login'
login_manager.login_message = "Please log in to access the requested resource."
login_manager.login_message_category = "info"

from hkabtrak.views import root_bp
from hkabtrak.absences.views import absences_bp
from hkabtrak.staff.views import staff_bp
from hkabtrak.course.views import courses_bp
from hkabtrak.admin.views import admin_bp
from hkabtrak.semester.views import semester_bp
app = Flask(__name__, instance_relative_config=True)
app.register_blueprint(root_bp, url_prefix='/')
app.register_blueprint(absences_bp, url_prefix='/absences')
app.register_blueprint(staff_bp, url_prefix='/staff')
app.register_blueprint(courses_bp, url_prefix='/courses')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(semester_bp, url_prefix='/semester')


# App Factory
def create_app(cf=None):
    print("config at: " + cf)
    app.config.from_pyfile(cf)

    # Initialize models
    from hkabtrak import models

    initialize_extensions(app)
    register_blueprints(app)

    # Register custom CLI command
    register_commands(app)

    return app


def register_commands(app):
    @app.cli.command("create-admin")
    def create_admin():
        """Create the default admin user."""
        from hkabtrak.models import User  # Make sure this import is inside the function to avoid early import issues
        admin_email = "admin@example.com"
        default_password = "admin123"

        # Check if the admin user already exists
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            new_admin = User(
                email=admin_email,
                password=default_password,
                name="Default Admin",
                user_type="A"
            )
            db.session.add(new_admin)
            db.session.commit()
            print("Default admin user created")
        else:
            print("Admin user already exists")


# Initialize Extensions
def initialize_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)


# Register Blueprints
def register_blueprints(app):
    from hkabtrak import views
