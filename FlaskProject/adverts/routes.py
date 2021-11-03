import math
from flask import render_template, url_for, flash,redirect, request, abort, Blueprint, current_app
from flask_login import current_user, login_required
from FlaskProject import db
from FlaskProject.models import Post, User, Bid
from FlaskProject.adverts.forms import AdvertForm, EmailForm, BidForm
from FlaskProject.users.utils import save_ad_picture, delete_ad_picture, send_contact_email, processbid, check_time, expire_email
from FlaskProject.main.routes import home
from FlaskProject.main.forms import HomeFilter
from sqlalchemy import text

adverts=Blueprint('adverts', __name__)

@adverts.route("/advert/<int:advert_id>")
def advert(advert_id):
    advert=Post.query.get_or_404(advert_id)
    currentbid=Bid.query.filter_by(post_id=advert.id).filter_by(highest_bid=True).first()
    if not advert.bid:
        form=EmailForm()
    else:
        form=BidForm()
    if currentbid:
        biduser=User.query.filter_by(id=currentbid.user_bid_id).first()
        remaining=check_time(advert)
        if remaining.days>2:
            expire_email(currentbid, advert, biduser)
            current_app.config['LOGIN_DISABLED'] = True
            advert.expired=True
            db.session.commit()
            delete_advert(advert_id)
            current_app.config['LOGIN_DISABLED'] = False
            return render_template('expired.html', title="Expired Advert")
        return render_template('advert.html', title=advert.title, advert=advert, form=form, bid=currentbid, user=biduser)
    return render_template('advert.html', title=advert.title, advert=advert, form=form, bid=currentbid)

@adverts.route("/advert/<int:advert_id>/update", methods=['GET', 'POST'])
@login_required
def update_advert(advert_id):
    advert=Post.query.get_or_404(advert_id)
    if advert.author != current_user and current_user.email != "elliot@valeviews.com":
        abort(403)
    form=AdvertForm()
    if form.validate_on_submit():
        advert.title=form.title.data
        advert.content=form.content.data
        advert.price=form.price.data
        advert.product=form.product.data
        advert.manufacturer=form.manufacturer.data
        advert.bid=form.bid.data
        if form.picture.data:
            picture_file=save_ad_picture(form.picture.data)
            delete_ad_picture(advert)
            advert.advert_image=picture_file
        db.session.commit()
        flash('Your Advert has been Updated!', 'success')
        return redirect(url_for('adverts.advert', advert_id=advert.id))
    elif request.method == 'GET':
        form.title.data=advert.title
        form.content.data=advert.content
        form.price.data=advert.price
        form.product.data=advert.product
        form.manufacturer.data=advert.manufacturer
        form.picture.data=advert.advert_image
        form.bid.data=advert.bid
    return render_template('create_advert.html', title='Update Advert', form=form, legend='Update Advert')

@adverts.route("/advert/new", methods=['GET', 'POST'])
@login_required
def new_advert():
    form = AdvertForm()
    if form.submit.data:
        if form.manufacturer.data == None or form.product.data == None:
            flash("You Must Select a Manufacturer and Product Filter", "danger")
        latest_advert=Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).first()
        if form.validate_on_submit() and latest_advert.date_posted.seconds != form.date_posted.seconds:
            advert=Post(title=form.title.data, content=form.content.data, price=form.price.data, product=form.product.data, manufacturer=form.manufacturer.data, bid=form.bid.data, author=current_user)
            if form.picture.data:
                picture_file=save_ad_picture(form.picture.data)
                advert.advert_image=picture_file
            db.session.add(advert)
            db.session.commit()
            flash('Your Advert has been Successfully Created!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Dont Post Too Many Consecutive Adverts!', 'danger')
    return render_template('create_advert.html', title='New Advert', form=form, legend='New Advert')

@adverts.route("/advert/<int:advert_id>/delete", methods=['POST'])
@login_required
def delete_advert(advert_id):
    advert=Post.query.get_or_404(advert_id)
    expired=advert.expired
    if advert.author != current_user and not advert.expired and current_user.email != "elliot@valeviews.com":
        abort(403)
    delete_ad_picture(advert)
    bids=Bid.query.filter_by(post_id = advert.id)
    for i in bids:
        db.session.delete(i)
    db.session.delete(advert)
    db.session.commit()
    if not expired:
        flash('Your Advert has been Deleted!', 'success')
    return redirect(url_for('main.home'))

@adverts.route("/advert/<int:advert_id>", methods=['GET', 'POST'])
def interest(advert_id):
    advert=Post.query.get_or_404(advert_id)
    if not advert.bid:
        form = EmailForm()
        if form.validate_on_submit():
            send_contact_email(form, advert)
            flash('An Email has been sent showing your interest!', 'info')
        else:
            flash('Invalid Message, Please try again using less characters and less "Enter" characters', 'danger')
    else:
        form = BidForm()
        if form.validate_on_submit():
            validate=processbid(form, advert)
            if validate:
                flash('Your bid has been submitted!', 'info')
            else:
                flash('Your Bid was Invalid, Please try again', 'danger')
        else:
            flash('Your Bid was Invalid, Please try again', 'danger')
        
        
    return redirect(url_for('adverts.advert', advert_id=advert.id))

def sort(adverts, form):
    page = request.args.get('page', 1, type=int)
    sortdata=None
    if form.sort.data:
        if form.sort.data == "date_posted.desc()":
            adverts=adverts.order_by(Post.date_posted.desc())
            sortdata="Date-Newest"
        if form.sort.data == "date_posted.asc()":
            adverts=adverts.order_by(Post.date_posted.asc())
            sortdata="Date-Oldest"
        if form.sort.data == "price.asc()":
            adverts=adverts.order_by(Post.price.desc())
            sortdata="Price-High-Low"
        if form.sort.data == "price.desc()":
            adverts=adverts.order_by(Post.price.asc())
            sortdata="Price-Low-High"
        adverts=adverts.paginate(page=page, per_page=5)
    return adverts, sortdata

@adverts.route("/filters", methods=['POST'])
def filters():
    form=HomeFilter()
    if not form:
        abort(403)
    if form.validate_on_submit:
        if form.product.data != None and form.manufacturer.data != None:
            adverts=Post.query.filter_by(product=form.product.data)\
                .filter_by(manufacturer=form.manufacturer.data)
        elif form.product.data != None and form.manufacturer.data == None:
            adverts=Post.query.filter_by(product=form.product.data)
        elif form.manufacturer.data != None and form.product.data == None:
            adverts=Post.query.filter_by(manufacturer=form.manufacturer.data)
        else:
            adverts=Post.query.filter_by(id=Post.id)
        adverts, sortdata=sort(adverts, form)
    return render_template('filters.html', adverts=adverts, form=form, homepage=True, sortdata=sortdata)