import io
import os

import dropbox
from flask import Blueprint, redirect, render_template, request, url_for

from .extensions import db
from .models import User

access_token = os.getenv("DROPBOX_TOKEN")
refresh_token = os.getenv("REFRESH_TOKEN")
app_key = os.getenv("APP_KEY")
app_secret = os.getenv("REFRESH_TOKEN")



main = Blueprint('main', __name__)

@main.route('/')
def index():
    users = User.query.all()
    users_list_html = [f"<li>{ user.username }</li>" for user in users]
    f"<ul>{''.join(users_list_html)}</ul>"
    
    return render_template('upload.html')

@main.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        dbx = dropbox.Dropbox(
            oauth2_access_token=access_token,
            app_key = app_key,
            app_secret = app_secret
            # oauth2_refresh_token = ""
        )
        filename = file.filename
        file_stream = io.BytesIO(file.read())
        dropbox_destination = "/"
        try:
            dbx.files_upload(file_stream.getvalue(), f'/{filename}')
            shared_link_metadata = dbx.sharing_create_shared_link(dropbox_destination)
            
            url = shared_link_metadata
            print( url)
            return 'File uploaded successfully'
        except dropbox.exceptions.ApiError as err:
            return f'Failed to upload file: {err}'


@main.route('/add/<username>')
def add_user(username):
    db.session.add(User(username=username))
    db.session.commit()
    return redirect(url_for("main.index"))

