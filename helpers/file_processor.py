import os
import pandas as pd

from . import breezy
from . import google_drive


def get_new_url(my_session, old_url):
    result = breezy.download_file_single_session(my_session, old_url)
    if result[1] is False:
        new_url = "Unable to open resume link"
        return new_url
    else:
        file_name = result[0]
        print("File Name", file_name)
        new_url = google_drive.upload_file_to_drive(file_name)
    return new_url


def process_spreadsheet(file_name):
    my_session = breezy.sign_in()
    # sample_breezy_file.csv
    file_path = os.path.join("spreadsheets", file_name)
    if ".csv" in file_name[-5:]:
        df = pd.read_csv(file_path)
    else:
        # Considering Excel file (xlsx)
        df = pd.read_excel(file_path)
    df["resume permalink"] = df["resume"].apply(lambda x: get_new_url(my_session, x))
    save_file_name = "Updated_" + file_name
    save_file_path = os.path.join("spreadsheets", save_file_name)
    df.to_csv(save_file_path, index=False)
    return save_file_name



