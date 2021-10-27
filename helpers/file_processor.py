import os
import pandas as pd

from . import breezy
from . import google_drive
from . import mail

from threading import Thread


def get_new_url(my_session, old_url, access_token, user_refresh_token):
    result = breezy.download_file_single_session(my_session, old_url)
    if result[1] is False:
        new_url = "Unable to open resume link"
        return new_url
    else:
        file_name = result[0]
        print("File Name", file_name)
        new_url = google_drive.upload_file_to_drive(file_name, access_token, user_refresh_token)
    return new_url


def cleanse_zip_code(x):
    x = str(x)
    digits_missing = 5 - len(x)
    x = "0" * digits_missing + x
    return x


def add_county_and_zip(df):
    original_columns = list(df.columns)
    if "location" in original_columns:
        county_zip_file_path = os.path.join("static_data", "city-state-county-zip.pickle")
        dfp = pd.read_pickle(county_zip_file_path)
        df["location_lower"] = df["location"].apply(lambda x: x.lower())
        df = df.merge(dfp, left_on="location_lower", right_on="location", how="left")
        df = df.rename(columns={"location_x": "location"})
        df = df[original_columns + ["county", "zip"]]
        df["zip"] = df["zip"].apply(lambda x: cleanse_zip_code(x))
    return df


def process_spreadsheet(file_name, access_token, user_refresh_token, user_name, user_email):
    my_session = breezy.sign_in()
    # sample_breezy_file.csv
    file_path = os.path.join("spreadsheets", file_name)
    if ".csv" in file_name[-5:]:
        df = pd.read_csv(file_path)
    else:
        # Considering Excel file (xlsx)
        df = pd.read_excel(file_path)
    df["resume permalink"] = df["resume"].apply(lambda x: get_new_url(my_session, x, access_token, user_refresh_token))
    save_file_name = "Updated_" + file_name
    save_file_path = os.path.join("spreadsheets", save_file_name)
    df = add_county_and_zip(df)
    df.to_csv(save_file_path, index=False)
    # name, email = google_drive.get_user_info(access_token)
    mail.send_mail(user_name, user_email, [save_file_path])
    print("save_file_path: ", save_file_path)
    print("os.path.exists(save_file_path): ", os.path.exists(os.path.join(os.getcwd(), "spreadsheets", file_name)))
    if os.path.exists(os.path.join(os.getcwd(), "spreadsheets", file_name)):
        os.remove(os.path.join(os.getcwd(), "spreadsheets", file_name))
        print("Deleted file: ", os.path.join(os.getcwd(), "spreadsheets", file_name))
    if os.path.exists(os.path.join(os.getcwd(), "spreadsheets", save_file_name)):
        os.remove(os.path.join(os.getcwd(), "spreadsheets", save_file_name))
        print("Deleted file: ", os.path.join(os.getcwd(), "spreadsheets", save_file_name))
    return save_file_name


def file_handler(file_name, access_token, user_refresh_token, user_name, user_email):
    worker = Thread(target=process_spreadsheet, args=(file_name, access_token, user_refresh_token, user_name, user_email,))
    worker.daemon = True
    worker.start()

