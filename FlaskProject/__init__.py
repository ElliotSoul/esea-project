from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from FlaskProject.config import Config
from flask_s3 import FlaskS3

db=SQLAlchemy()
bcrypt=Bcrypt()
login_manager=LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
s3 = FlaskS3()

mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    #with app.app_context():
    #    db.create_all()
    s3.init_app(app)
    app.config['FLASKS3_BUCKET_NAME'] = 'eseaproject'

    from FlaskProject.users.routes import users
    from FlaskProject.adverts.routes import adverts
    from FlaskProject.main.routes import main
    from FlaskProject.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(adverts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
app=create_app()