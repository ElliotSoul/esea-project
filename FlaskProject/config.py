import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_KEY = os.environ.get('S3_KEY')
    S3_SECRET = os.environ.get('S3_SECRET')
    ACL = 'public-read'
    FLASKS3_BUCKET_NAME = S3_BUCKET
    FLASKS3_REGION = 'eu-west-2'
    LOGIN_DISABLED = False
    BUCKET_URL_PFP=os.environ.get('BUCKET_URL_PFP')
    BUCKET_URL_AD=os.environ.get('BUCKET_URL_AD')