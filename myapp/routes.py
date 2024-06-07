from flask import Blueprint, redirect, url_for, render_template

from .extensions import db
from .models import User

main = Blueprint('main', __name__)

@main.route('/')
def index():
    users = User.query.all()
    users_list_html = [f"<li>{ user.username }</li>" for user in users]
    f"<ul>{''.join(users_list_html)}</ul>"
    return render_template('upload.html')




@main.route('/add/<username>')
def add_user(username):
    db.session.add(User(username=username))
    db.session.commit()
    return redirect(url_for("main.index"))

