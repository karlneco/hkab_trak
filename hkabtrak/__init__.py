from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

####################################################
# Config
####################################################
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'root.index'


####################################################
# App Factory
####################################################
def create_app(cf=None):
    print("config at: " + cf)
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(cf)

    from hkabtrak import models

    initialize_extensions(app)
    register_blueprints(app)
    return app


# attach app
def initialize_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)


# load blue  prints
def register_blueprints(app):
    from hkabtrak.views import root_bp
    from hkabtrak.absences.views import absences_bp
    from hkabtrak.teacher.views import teachers_bp
    from hkabtrak.course.views import courses_bp
    from hkabtrak.admin.views import admin_bp

    app.register_blueprint(root_bp, url_prefix='/')
    app.register_blueprint(absences_bp, url_prefix='/absences')
    app.register_blueprint(teachers_bp, url_prefix='/teacher')
    app.register_blueprint(courses_bp, url_prefix='/courses')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    from hkabtrak import views
