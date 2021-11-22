import os
import secrets
from PIL import Image
from datetime import datetime
from flask import url_for, current_app
from flask_mail import Message
from FlaskProject import mail, db, s3
from flask_login import current_user
from FlaskProject.models import Bid, User, Post
from FlaskProject.config import Config
from wtforms.validators import ValidationError
import boto3

def save_picture(form_picture):
    random_filename = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_filename=random_filename+f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_filename)
    final_size=(125, 125)
    with Image.open(form_picture) as img:
        img.thumbnail(final_size)
        img.save(picture_path)
        s3 = boto3.resource('s3')
        s3.client.upload_file(form_picture, Config.S3_BUCKET, 'static/profile_pics/'+str(picture_filename))
        prev_picture = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image_file)
        if os.path.exists(prev_picture) and os.path.basename(prev_picture) != 'default.jpg':
            os.remove(prev_picture) 
    return picture_filename

def save_ad_picture(form_picture):
    random_filename = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_filename=random_filename+f_ext
    picture_path = os.path.join(current_app.root_path, 'https://eseaproject.s3.amazonaws.com/static/advert_pics', picture_filename)
    final_size=(250, 250)
    with Image.open(form_picture) as img:
        img.thumbnail(final_size)
        rgb_img = img.convert('RGB')
        rgb_img.save(picture_path)

    return picture_filename

def delete_ad_picture(advert):
    prev_picture = os.path.join(current_app.root_path, 'https://eseaproject.s3.amazonaws.com/static/advert_pics', advert.advert_image)
    if os.path.exists(prev_picture) and os.path.basename(prev_picture) != 'defaultad.jpg':
        os.remove(prev_picture)

def processbid(form, advert):
    currentbid=Bid.query.filter_by(post_id=advert.id)\
                        .filter_by(highest_bid=True).first()
    previousbid=Bid.query.filter_by(post_id=advert.id)\
                        .filter_by(user_bid_id=current_user.id).first()
    if currentbid:
        if form.bid.data > currentbid.price:
            advert_bid=Bid(post_id=advert.id, user_bid_id=current_user.id, price=form.bid.data, highest_bid=True)
            advert_user=User.query.filter_by(id=currentbid.user_bid_id).first()
            currentbid.highest_bid=False
            db.session.add(advert_bid)
            if previousbid:
                db.session.delete(previousbid)
            db.session.commit()
            out=send_outbid_email(currentbid, advert_bid, advert_user, advert)
            return True
        else:
            return False
    else:
        advert_bid=Bid(post_id=advert.id, user_bid_id=current_user.id, price=form.bid.data, highest_bid=True)
        db.session.add(advert_bid)
        db.session.commit()
        return True

def check_time(advert):
    current_time=datetime.now()
    advert_time=advert.date_posted
    remaining=current_time-advert_time
    return remaining

def send_reset_email(user):
    token=user.get_reset_token()
    msg=Message('Esea Password Reset Request', sender='noreply@esea.com', recipients=[user.email])
    msg.body= f'''To Reset your Password, visit the following link:

{url_for('users.reset_token', token=token, _external=True)}

If you didnt make this request, ignore this email and nothing will be changed

The Email (noreplyprojectalevelproject) Has an unmonitored inbox, any emails sent to this email will not be seen or answered.
'''
    mail.send(msg)

def send_contact_email(form, advert):
    msg=Message('Esea Interest in Product Declared', sender=current_user.email, recipients=[advert.author.email])
    assert msg.sender == current_user.email
    msg.body=f'''Hello {advert.author.username}!
User: {current_user.username}, is interested in your post:

{advert.title}

They Said:

{form.message.data}

Please send your reply to: {current_user.email}


The Email (noreplyprojectalevelproject) Has an unmonitored inbox, any emails sent to this email will not be seen or answered.
'''
    mail.send(msg)

def send_outbid_email(currentbid, advert_bid, advert_user, advert):
    msg=Message('Esea Outbid of Product', sender='noreply@esea.com', recipients=[advert_user.email])
    msg.body=f'''Hello {advert_user.username}!
User: {current_user.username}, Has unfortunately Outbid you on Product: {advert.title}

Your Bid: {currentbid.price}
Their Bid: {advert_bid.price}

Click Here to View the Product!:
{url_for('adverts.advert', advert_id=advert.id, _external=True)}

The Email (noreplyprojectalevelproject) Has an unmonitored inbox, any emails sent to this email will not be seen or answered.
'''
    mail.send(msg)
    return True

def expire_email(currentbid, advert, biduser):
    msg=Message('Esea Bid Product Expired', sender='noreply@esea.com', recipients=[advert.author.email])
    msg.body=f'''Hello {advert.author.username}!
Your Listed Product: {advert.title}, has expired after bid on for 3 Days.

Highest Bid: {currentbid.price} from {biduser.username}.

Please Email {biduser.email} to contact them on their Highest Bid!

The Email (noreplyprojectalevelproject) Has an unmonitored inbox, any emails sent to this email will not be seen or answered.
'''
    mail.send(msg)
    msg=Message('Esea Bid Product Ended', sender='noreply@esea.com', recipients=[biduser.email])
    msg.body=f'''Hello {biduser.username}!
The Listed Product: {advert.title}, has ended with your bid winning!

Your Bid: {currentbid.price}

Please Email await an email from {advert.author.username} about the product!

The Email (noreplyprojectalevelproject) Has an unmonitored inbox, any emails sent to this email will not be seen or answered.
'''
    mail.send(msg)