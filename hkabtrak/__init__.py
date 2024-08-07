import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

# Define global instances of extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app(config_filename=None):
    # Create a new Flask app instance
    app = Flask(__name__, instance_relative_config=True)

    if config_filename:
        # Load the specified configuration file
        app.config.from_pyfile(config_filename)

    # Check if we are in testing mode
    if app.config.get('TESTING', False):
        # Use a default secret key for testing
        app.config['SECRET_KEY'] = 'test-secret-key'
    else:
        # Override the SECRET_KEY with the value from the environment variable
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key:
            raise RuntimeError('SECRET_KEY environment variable is not set. The application cannot start without it.')
        app.config['SECRET_KEY'] = secret_key

        # Read email configuration from environment variables
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.example.com')
        app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 465))
        app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'False') == 'False'
        app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'True') == 'True'
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
        app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    # Set up login manager settings
    login_manager.login_view = 'staff.staff_login'
    login_manager.login_message = "Please log in to access the requested resource."
    login_manager.login_message_category = "info"

    # Initialize models
    from hkabtrak import models

    # Register blueprints
    register_blueprints(app)

    # Register custom CLI commands
    register_commands(app)

    return app

def register_blueprints(app):
    from hkabtrak.views import root_bp
    from hkabtrak.absences.views import absences_bp
    from hkabtrak.staff.views import staff_bp
    from hkabtrak.course.views import courses_bp
    from hkabtrak.admin.views import admin_bp
    from hkabtrak.semester.views import semester_bp

    app.register_blueprint(root_bp, url_prefix='/')
    app.register_blueprint(absences_bp, url_prefix='/absences')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(courses_bp, url_prefix='/courses')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(semester_bp, url_prefix='/semester')

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
