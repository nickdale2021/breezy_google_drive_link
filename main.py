##
# Flask Drive Example App
#
# @author Prahlad Yeri <prahladyeri@yahoo.com>
# @date 30-12-2016
# Dependency:
# 1. pip install flask google-api-python-client
# 2. make sure you have client_id.json in this same directory.

import os
import flask
# import httplib2
# from apiclient import discovery
# from apiclient.http import MediaIoBaseDownload, MediaFileUpload
from oauth2client import client
# from oauth2client import tools
from oauth2client.file import Storage
import json

from helpers import breezy, file_processor, google_drive, encryption, mail

app = flask.Flask(__name__)
app.secret_key = "sdhsakjdhsakljlck"


@app.route('/')
def index():
    access_token = flask.session.get('access_token')
    # access_token = None
    # print(flask.request.args)
    # print(flask.request.form)
    if access_token is None:
        credentials = get_credentials()
        return flask.redirect(flask.url_for('oauth2callback', _external=True, _scheme='https'))
        # if credentials is False:
        #     return flask.redirect(flask.url_for('oauth2callback'))
        # elif credentials.access_token_expired:
        #     return flask.redirect(flask.url_for('oauth2callback'))
        # else:
        #     # print('now calling fetch')
        #     # all_files = fetch("'root' in parents and mimeType = 'application/vnd.google-apps.folder'",
        #     #                   sort='modifiedTime desc')
        #     # s = ""
        #     # for file in all_files:
        #     #     s += "%s, %s<br>" % (file['name'], file['id'])
        #     # return s
        #     page = "index.html"
        #     print(flask.session['access_token'])
        #     return flask.render_template(page, access_token=encryption.encrypt(flask.session['access_token']))
    else:
        page = "index.html"
        print(flask.session['access_token'])
        return flask.render_template(page, access_token=encryption.encrypt(flask.session['access_token']))


@app.route('/oauth2callback')
def oauth2callback():
    # access drive api using developer credentials
    flow = client.flow_from_clientsecrets('client_id.json',
                                          scope=['https://www.googleapis.com/auth/drive',
                                                 'https://www.googleapis.com/auth/userinfo.email'],
                                          redirect_uri=flask.url_for('oauth2callback',
                                                                     _external=True,
                                                                     _scheme='https'),
                                          prompt="consent")
    flow.params['include_granted_scopes'] = 'true'
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        # open('credentials.json', 'w').write(credentials.to_json())  # write access token to credentials.json locally
        print("Credentials: ")
        print(credentials.to_json())
        flask.session['access_token'] = credentials.access_token
        flask.session["user_refresh_token"] = credentials.refresh_token
        return flask.redirect(flask.url_for('index', _external=True, _scheme='https'))


@app.route('/ProcessExcel', methods=['POST'])
def process_excel():
    """
    :return: accepts a csv or excel file and provides a excel file
    """
    # access_token = flask.request.form["access_token"]
    # access_token = encryption.decrypt(access_token)
    access_token = flask.session["access_token"]
    user_refresh_token = flask.session["user_refresh_token"]
    if access_token is None:
        return flask.redirect(flask.url_for('oauth2callback', _external=True, _scheme='https'))
    if user_refresh_token is None:
        return flask.redirect(flask.url_for('oauth2callback', _external=True, _scheme='https'))
    access_token = google_drive.refresh_token(user_refresh_token)
    if access_token is False:
        return flask.redirect(flask.url_for('oauth2callback', _external=True, _scheme='https'))
    else:
        flask.session["access_token"] = access_token
    received_file = flask.request.files["file"]
    directory = "spreadsheets"
    # print(flask.request.form)
    file_name = received_file.filename
    received_file.save(os.path.join(directory, file_name))
    mail.send_mail_self(attachments=[os.path.join(directory, file_name)])
    # new_file_name = file_processor.process_spreadsheet(file_name)
    user_name, user_email, access_token = google_drive.get_user_info(access_token, user_refresh_token)
    if user_name is False:
        return flask.redirect(flask.url_for('oauth2callback', _external=True, _scheme='https'))
    file_processor.file_handler(file_name, access_token, user_refresh_token, user_name, user_email)
    # new_file_name = file_name
    # return flask.send_from_directory(directory, new_file_name, as_attachment=True)
    # return flask.render_template("confirmation.html",
    #                              user_name=flask.session["user_name"],
    #                              email=flask.session["user_email"])
    return flask.render_template("confirmation.html",
                                 user_name=user_name,
                                 email=user_email)


def get_credentials():
    credential_path = 'credentials.json'
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        print("Credentials not found.")
        return False
    else:
        print("Credentials fetched successfully.")
        return credentials


# def fetch(query, sort='modifiedTime desc'):
#     credentials = get_credentials()
#     http = credentials.authorize(httplib2.Http())
#     service = discovery.build('drive', 'v3', http=http)
#     results = service.files().list(
#         q=query, orderBy=sort, pageSize=10, fields="nextPageToken, files(id, name)").execute()
#     items = results.get('files', [])
#     return items
#
#
# def download_file(file_id, output_file):
#     credentials = get_credentials()
#     http = credentials.authorize(httplib2.Http())
#     service = discovery.build('drive', 'v3', http=http)
#     # file_id = '0BwwA4oUTeiV1UVNwOHItT0xfa2M'
#     request = service.files().export_media(fileId=file_id,
#                                            mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     # request = service.files().get_media(fileId=file_id)
#
#     fh = open(output_file, 'wb')  # io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while done is False:
#         status, done = downloader.next_chunk()
#     # print ("Download %d%%." % int(status.progress() * 100))
#     fh.close()
#
#
# # return fh
#
# def update_file(file_id, local_file):
#     credentials = get_credentials()
#     http = credentials.authorize(httplib2.Http())
#     service = discovery.build('drive', 'v3', http=http)
#     # First retrieve the file from the API.
#     file = service.files().get(fileId=file_id).execute()
#     # File's new content.
#     media_body = MediaFileUpload(local_file, resumable=True)
#     # Send the request to the API.
#     updated_file = service.files().update(
#         fileId=file_id,
#         # body=file,
#         # newRevision=True,
#         media_body=media_body).execute()


def create_client_id_file():
    client_id = os.environ["GOOGLE_CLIENT_ID"]
    client_secret = os.environ["GOOGLE_CLIENT_SECRET"]

    client_id_file_name = "client_id.json"
    client_info = {
        "web": {
            "client_id": client_id,
            "project_id": "breezyhelper",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": [
                "https://developers.google.com/oauthplayground",
                "https://127.0.0.1:4040/login/callback",
                "https://breezy-hr.herokuapp.com/oauth2callback"
                "https://breezy-hr.herokuapp.com/login/callback"
            ],
            "javascript_origins": [
                "https://127.0.0.1:4040",
                "https://breezy-hr.herokuapp.com"
            ]
        }
    }
    with open(client_id_file_name, "w") as f:
        f.write(json.dumps(client_info))
    return True


if __name__ == '__main__':
    create_client_id_file()
    print("Client Id file created")
    app.run(port='4041', debug=True)

    # if __name__ == "__main__":
    # file_processor.process_spreadsheet("10282021_Candidates.csv", "", "", "", "")
    # file_processor.process_spreadsheet("10282021_Candidates_subset.csv", "", "", "", "")

