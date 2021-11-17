from flask.cli import with_appcontext
@with_appcontext
def create_tables():
    db.create_all()