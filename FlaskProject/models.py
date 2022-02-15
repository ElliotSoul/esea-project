from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from FlaskProject import db, login_manager
from flask_login import UserMixin
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20), unique=True, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    image_file=db.Column(db.String(20), nullable=False, default='default.jpg')
    password=db.Column(db.String(60), nullable=False)
    posts=db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(20), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content=db.Column(db.Text, nullable=False)
    price=db.Column(db.Numeric(7,2), nullable=False)
    advert_image=db.Column(db.String(20), nullable=False, default='defaultad.jpg')
    manufacturer=db.Column(db.String(10), nullable=False)
    product=db.Column(db.String(20), nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bid=db.Column(db.Boolean, nullable=False)
    expired=db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id=db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_bid_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price=db.Column(db.Numeric(7,2), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    highest_bid = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"Post('{self.price}', '{self.date_posted}')"

