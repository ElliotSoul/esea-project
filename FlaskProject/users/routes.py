from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from FlaskProject import db, bcrypt
from FlaskProject.models import User, Post, Bid
from FlaskProject.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,RequestResetForm, ResetPasswordForm)
from FlaskProject.users.utils import save_picture, send_reset_email
from FlaskProject.config import Config

users=Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created! Feel Free to Login!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful, Please Check your Email and Password', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file=save_picture(form.picture.data)
            current_user.image_file=picture_file
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Successfully Updated your Details', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
    return render_template('account.html', title='Account', form=form, bucket_url_pfp=Config.BUCKET_URL_PFP)

@users.route("/user/<string:username>")
def user_adverts(username):
    page = request.args.get('page', 1, type=int)
    user=User.query.filter_by(username=username).first_or_404()
    adverts=Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template("user_adverts.html", adverts=adverts, user=user, bucket_url_pfp=Config.BUCKET_URL_PFP, bucket_url_ad=Config.BUCKET_URL_AD)

@users.route("/user/<string:username>/bids")
@login_required
def user_bids(username):
    page = request.args.get('page', 1, type=int)
    user=User.query.filter_by(username=username).first_or_404()
    if user != current_user:
        abort(403)
    bidadverts=Post.query.join(Bid, Post.id == Bid.post_id).filter(Bid.user_bid_id == user.id)
    adverts=bidadverts.order_by(Post.id)\
            .paginate(page=page, per_page=5)
    return render_template("bid_adverts.html", adverts=adverts, user=user, bucket_url_pfp=Config.BUCKET_URL_PFP, bucket_url_ad=Config.BUCKET_URL_AD)

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An Email has been sent with instructions to Reset your Password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('That Token is Invalid or has Expired', 'warning')
        return redirect(url_for('users.reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()
        flash(f'Password Changed Successfully', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
