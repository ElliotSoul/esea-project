from flask import render_template, request, Blueprint
from FlaskProject.models import Post, Bid
from FlaskProject.main.forms import HomeFilter

main=Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    adverts=Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    form=HomeFilter()
    test="https://eseaproject.s3.eu-west-2.amazonaws.com/static/profile_pics/"
    return render_template("home.html", adverts=adverts, form=form, homepage=True, test=test)

@main.route("/about")
def about():
    return render_template("about.html", title="Contact Us")