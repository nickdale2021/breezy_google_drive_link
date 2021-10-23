import os
import flask
import requests


def get_user_info(access_token, user_refresh_token):
    # access_token = flask.session["access_token"]
    r = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            params={'access_token': access_token})
    print("Fetching User Info")
    print(r.status_code)
    print(r.content)
    if r.status_code == 401:
        access_token = refresh_token(user_refresh_token)
        r = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            params={'access_token': access_token})
        print("Fetching User Info")
        print(r.status_code)
        print(r.content)

    # name = r.json()["name"]
    name = r.json()["email"]
    email = r.json()["email"]
    # flask.session["user_name"] = name
    # flask.session["user_email"] = email
    print(name, email)
    return name, email


def refresh_token(user_refresh_token):
    client_id = os.environ["GOOGLE_CLIENT_ID"]
    client_secret = os.environ["GOOGLE_CLIENT_SECRET"]

    api_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": user_refresh_token
    }
    x = requests.post(url=api_url, data=data)
    print("Refreshing Token: ", end=" ")
    print(x.status_code)
    print(x.json())
    if x.status_code == 200:
        return x.json()["access_token"]
    else:
        print("Access Token expired. Need to login again!")
        return flask.redirect(flask.url_for('oauth2callback'))


def upload_file_to_drive(file_name, access_token, user_refresh_token):
    file_id = upload_file_params(file_name, access_token, user_refresh_token)
    is_success = rename_file_params(file_id, file_name, access_token, user_refresh_token)
    is_success = make_public_params(file_id, access_token, user_refresh_token)
    return_url = get_file_url_params(file_id, access_token, user_refresh_token)
    return return_url


def upload_file_params(file_name, access_token, user_refresh_token):
    # access_token = flask.session["access_token"]
    # user_refresh_token = flask.session["user_refresh_token"]
    api_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=media"
    file_path = os.path.join("resumes", file_name)
    with open(file_path, "rb") as f:
        file_data = f.read()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/pdf"
    }
    x = requests.post(url=api_url, data=file_data, headers=headers)
    print("Uploading File to google drive: Attempt 1")
    print(x.status_code)
    print(x.json())
    if x.status_code != 200:
        access_token = refresh_token(user_refresh_token)
        # flask.session["access_token"] = access_token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/pdf"
        }
        x = requests.post(url=api_url, data=file_data, headers=headers)
        print("Uploading File to google drive: Attempt 2 - after token refresh")
        print(x.status_code)
        print(x.json())
    file_id = x.json()["id"]
    os.remove(file_path)
    return file_id


def rename_file_params(file_id, file_name, access_token, user_refresh_token):
    # access_token = flask.session["access_token"]
    # user_refresh_token = flask.session["user_refresh_token"]
    api_url = "https://www.googleapis.com/drive/v3/files/" + file_id
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "name": file_name,
        "mimeType": "application/pdf"
    }
    x = requests.patch(url=api_url, headers=headers, json=data)
    if x.status_code != 200:
        access_token = refresh_token(user_refresh_token)
        # flask.session["access_token"] = access_token
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        x = requests.patch(url=api_url, headers=headers, json=data)
    return True


def make_public_params(file_id, access_token, user_refresh_token):
    # access_token = flask.session["access_token"]
    # user_refresh_token = flask.session["user_refresh_token"]
    api_url = f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "role": "reader",
        "type": "anyone"
    }
    x = requests.post(url=api_url, json=data, headers=headers)
    if x.status_code != 200:
        access_token = refresh_token(user_refresh_token)
        # flask.session["access_token"] = access_token
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        x = requests.post(url=api_url, json=data, headers=headers)
    return True


def get_file_url_params(file_id, access_token, user_refresh_token):
    # access_token = flask.session["access_token"]
    # user_refresh_token = flask.session["user_refresh_token"]
    api_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=webViewLink,parents"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    x = requests.get(url=api_url, headers=headers)
    if x.status_code != 200:
        access_token = refresh_token(user_refresh_token)
        flask.session["access_token"] = access_token
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        x = requests.get(url=api_url, headers=headers)

    return x.json()["webViewLink"]


# def upload_file():
#     file = ""
#     api_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=media"
#     # json_data = {
#     #     "parents": [],
#     #     "mimeType": "application/pdf",
#     #     "name": "",
#     #     "permissions": [{"type": "anyone"}],
#     #     "fileExtension": "pdf",
#     #     "originalFilename": ""
#     # }
#     with open(file, "rb") as f:
#         file_data = f.read()
#     headers = {
#         "Authorization": "Bearer ",
#         "Content-Type": "application/pdf"
#     }
#     # x = requests.post(url=api_url, files={"file": file}, data=json_data, headers=headers)
#     x = requests.post(url=api_url, data=file_data, headers=headers)
#     print(x.status_code)
#     print(x.json())
#     return x
#
#
# def upload_file_2():
#     file = ""
#     api_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=media"
#     # json_data = {
#     #     "parents": [],
#     #     "mimeType": "application/pdf",
#     #     "name": "",
#     #     "permissions": [{"type": "anyone"}],
#     #     "fileExtension": "pdf",
#     #     "originalFilename": ""
#     # }
#     # with open(file, "rb") as f:
#     #     file_data = f.read()
#     # with open("naming_convention.json", "rb") as f:
#     #     metadata_file = f.read()
#
#     files = [
#         ("file", ("naming_convention.json", open("naming_convention.json", "rb"), "application/json")),
#         ("file", (file, open(file, "rb"), "application/pdf"))
#     ]
#     headers = {
#         "Authorization": "Bearer "
#         , "Content-Type": "multipart/form-data"
#     }
#     # x = requests.post(url=api_url, files={"file": file}, data=json_data, headers=headers)
#     x = requests.post(url=api_url, files=files, headers=headers)
#     print(x.status_code)
#     print(x.json())
#     return x
#
#
# def rename_file():
#     file_id = ""
#     api_url = "https://www.googleapis.com/drive/v3/files/" + file_id
#     headers = {
#         "Authorization": "Bearer "
#     }
#     data = {
#         "name": "",
#         "mimeType": "application/pdf",
#         "removeParents": [""],
#         "addParents": [""]
#     }
#     x = requests.patch(url=api_url, headers=headers, json=data)
#     print(x.status_code)
#     print(x.content)
#     return x
#
#
# # def upload_file():
# #     file = ""
# #     api_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=media"
# #     # json_data = {
# #     #     "parents": [],
# #     #     "mimeType": "application/pdf",
# #     #     "name": "",
# #     #     "permissions": [{"type": "anyone"}],
# #     #     "fileExtension": "pdf",
# #     #     "originalFilename": ""
# #     # }
# #     with open(file, "rb") as f:
# #         file_data = f.read()
# #     headers = {
# #         "Authorization": "Bearer ",
# #         "Content-Type": "application/pdf"
# #     }
# #     # x = requests.post(url=api_url, files={"file": file}, data=json_data, headers=headers)
# #     x = requests.post(url=api_url, data=file_data, headers=headers)
# #     print(x.status_code)
# #     print(x.json())
# #     return x
#
#
# def make_public():
#     file_id = "1r6dg9QYR8WOEk25M4C9MbnyHgUnmoGpJ"
#     api_url = f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions"
#     headers = {
#         "Authorization": "Bearer "
#     }
#     data = {
#         "role": "reader",
#         "type": "anyone"
#     }
#     x = requests.post(url=api_url, json=data, headers=headers)
#     print(x.status_code)
#     print(x.json())
#     return x
#
#
# def get_file_url():
#     file_id = "1r6dg9QYR8WOEk25M4C9MbnyHgUnmoGpJ"
#     api_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=webViewLink,parents"
#     headers = {
#         "Authorization": "Bearer "
#     }
#     x = requests.get(url=api_url, headers=headers)
#     print(x.status_code)
#     print(x.json())
#     return x
#
#
# def create_folder():
#     api_url = "https://www.googleapis.com/upload/drive/v3/files"
#     headers = {
#         "Authorization": "Bearer "
#     }
#     data = {"name": "foobar", "mimeType": "application/vnd.google-apps.folder"}
#     # x = requests.post(url=api_url, files={"file": file}, data=json_data, headers=headers)
#     x = requests.post(url=api_url, headers=headers, json=data)
#     print(x.status_code)
#     print(x.json())
#     return x
#
#
# def rename_folder():
#     file_id = "1FqTZzFjx60Ao3d_izUHDryAlAJvrAKyL"
#     api_url = "https://www.googleapis.com/drive/v3/files" + file_id
#     headers = {
#         "Authorization": "Bearer "
#     }
#     data = {
#         "name": "foobar",
#         "mimeType": "application/vnd.google-apps.folder"
#         # , "addParents": ["1WNPFyhAcPWRrgTynSDi7yVof6VjtcAdC"]
#     }
#     x = requests.patch(url=api_url, headers=headers, json=data)
#     print(x.status_code)
#     print(x.content)
#     return x
#
#
# def list_folders(folder_name):
#     api_url = "https://www.googleapis.com/drive/v3/files"
#     headers = {
#         "Authorization": "Bearer "
#     }
#     params = {
#         "q": f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
#     }
#     x = requests.get(url=api_url, headers=headers, params=params)
#     print(x.status_code)
#     print(x.json())
#     return x.json()


# def get_folder_id():
#     details = list_folders("upwork_uploads")
#     if len(details["files"]) > 0:
#         folder_id = details["files"][0]["id"]
#     else:


# if __name__ == "__main__":
#     refresh_token()
    # upload_file_2()
    # upload_file()
    # rename_file()
    # make_public()
    # get_file_url()
    # list_folders("upwork_uploads") # 175amDmJoj_JHCzZd4bCSUnYKBLx-nHXY
    # create_folder() # 1jxWm_M4S8ga2ID-2LxKqhepLvU-0g0I-
    # rename_folder()
