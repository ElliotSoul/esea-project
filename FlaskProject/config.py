import os

class Config:
    SECRET_KEY = 'a2da48312d87190b97db8652f2891b74'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///project.db'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    LOGIN_DISABLED = False
