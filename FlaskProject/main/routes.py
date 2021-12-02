from flask import render_template, request, Blueprint
from FlaskProject.models import Post, Bid
from FlaskProject.main.forms import HomeFilter
from FlaskProject.config import BUCKET_URL_AD, BUCKET_URL_PFP

main=Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    adverts=Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    form=HomeFilter()
    return render_template("home.html", adverts=adverts, form=form, homepage=True, bucket_url_pfp=BUCKET_URL_PFP, bucket_url_ad=BUCKET_URL_AD)

@main.route("/about")
def about():
    return render_template("about.html", title="Contact Us")