import io
import os
import os.path

import dropbox
from flask import Blueprint, redirect, render_template, request, url_for
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from .extensions import db
from .models import User

# access_token = os.getenv("DROPBOX_TOKEN")
# refresh_token = os.getenv("REFRESH_TOKEN")
# app_key = os.getenv("APP_KEY")
# app_secret = os.getenv("REFRESH_TOKEN")

SCOPES = ["https://www.googleapis.com/auth/drive"]

main = Blueprint('main', __name__)

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "myapp\credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=5432)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

try:
    service = build("drive", "v3", credentials=creds)

except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")




@main.route('/')
def index():
    users = User.query.all()
    users_list_html = [f"<li>{ user.username }</li>" for user in users]
    f"<ul>{''.join(users_list_html)}</ul>"
    

    return render_template('upload.html')


@main.route('/', methods=['POST'])
def upload_file():

    
    response = service.files().list(
        q="name='Test' and mimeType='application/vnd.google-apps.folder'",
        spaces = 'drive'
    ).execute()

    if not response['files']:
        file_metadata = {
            "name" : 'Test',
            "mimeType" : 'application/vnd.google-apps.folder'
        }

        file = service.files().create(body= file_metadata, fields="id").execute()

        folder_id = file.get('id')
    else: 
        folder_id = response['files'][0]['id']

    

    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        file_metadata = {
            "name": file.filename,
            "parents": [folder_id]
        }

        media = MediaFileUpload(file)
        upload_file = service.files().create(body=file_metadata,
                                             media_body = media, 
                                             fields="id" ).execute()
        
        print("Backed up file:" + file)

# ------------------- DROPBOX CODE ------------------------ #

# @main.route('/', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return 'No file part'
#     file = request.files['file']
#     if file.filename == '':
#         return 'No selected file'
#     if file:
#         dbx = dropbox.Dropbox(
#             oauth2_access_token=access_token,
#             app_key = app_key,
#             app_secret = app_secret
#             # oauth2_refresh_token = ""
#         )
#         filename = file.filename
#         file_stream = io.BytesIO(file.read())
#         dropbox_destination = "/"
#         try:
#             dbx.files_upload(file_stream.getvalue(), f'/{filename}')
#             shared_link_metadata = dbx.sharing_create_shared_link(dropbox_destination)
            
#             url = shared_link_metadata
#             print( url)
#             return 'File uploaded successfully'
#         except dropbox.exceptions.ApiError as err:
#             return f'Failed to upload file: {err}'


@main.route('/add/<username>')
def add_user(username):
    db.session.add(User(username=username))
    db.session.commit()
    return redirect(url_for("main.index"))

