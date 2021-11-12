import os

class Config:
    SECRET_KEY = 'a2da48312d87190b97db8652f2891b74'
    SQLALCHEMY_DATABASE_URI = 'postgresql://ylopxqibqhgttg:2a1c1a2777af1fe1b7548658d5bf68bea504513ede66693efed108647f3466ef@ec2-176-34-168-83.eu-west-1.compute.amazonaws.com:5432/ddpgtaobf1kfml'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    LOGIN_DISABLED = False