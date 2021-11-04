import os
import time
import requests
import pandas as pd

from . import breezy
from . import google_drive
from . import mail

from threading import Thread
from bs4 import BeautifulSoup

county_zip_dict = dict()


def get_county_zip_online(location_name):
    if len(str(location_name)) > 0:
        print("Checking Location:", location_name)
        if location_name in county_zip_dict.keys():
            print("Found in dictionary")
            return county_zip_dict[location_name]
        try:
            time.sleep(1.2)
            api = "https://www.unitedstateszipcodes.org/"
            form_data = {
                "q": str({location_name})
            }
            headers = {
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
            }
            s = requests.post(url=api, data=form_data, headers=headers)
            if s.status_code == 200:
                soup = BeautifulSoup(s.content, 'html.parser')
                try:
                    my_div = soup.find_all("div", {"id": "map-info"})[0]
                except Exception as E:
                    county_name = ""
                    zip_code = ""
                try:
                    county_name = my_div.find("tr").find("td").text
                    county_name = county_name.replace(" County", "")
                    county_name = county_name + "," + location_name.split(",")[-1]
                except Exception as E:
                    county_name = ""
                try:
                    try:
                        # Eg "Jolly, TX"
                        zip_code = my_div.find("h1").find("span").find("a").text
                    except AttributeError:
                        try:
                            # Eg "St. Rose, LA"
                            zip_code = my_div.find("h1").find("a").text
                        except:
                            zip_code = ""
                except Exception as E:
                    zip_code = ""
                county_zip_dict[location_name] = (county_name, zip_code)
                return county_name, zip_code
        except Exception as E:
            county_name = ""
            zip_code = ""
            county_zip_dict[location_name] = (county_name, zip_code)
            return county_name, zip_code
    else:
        county_name = ""
        zip_code = ""
        return county_name, zip_code


def get_new_url(my_session, old_url, access_token, user_refresh_token):
    if old_url == "":
        return ""
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
        county_zip_file_path = os.path.join("static_data", "city-state-county-zip-v2.pickle")
        dfp = pd.read_pickle(county_zip_file_path)
        df["location_lower"] = df["location"].apply(lambda x: x.lower())
        df = df.merge(dfp, left_on="location_lower", right_on="location", how="left")
        df = df.rename(columns={"location_x": "location"})
        df = df[original_columns + ["county", "zip"]]
        df = df.fillna("")
        df["zip"] = df["zip"].apply(lambda x: cleanse_zip_code(x))
    # for _, row in df.iterrows():
    #     print(row)
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
    df = df.fillna("")
    df["resume permalink"] = df["resume"].apply(lambda x: get_new_url(my_session, x, access_token, user_refresh_token))
    df = add_county_and_zip(df)
    for _, i in df.iterrows():
        if i["county"] == "":
            # print("Checking county and zip for", i["location"])
            county_name, zip_code = get_county_zip_online(i["location"])
            df["county"].iloc[_] = county_name
            df["zip"].iloc[_] = zip_code
            # time.sleep(1.2)
    save_file_name = "Updated_" + file_name
    save_file_path = os.path.join("spreadsheets", save_file_name)
    df.to_csv(save_file_path, index=False)
    print("save_file_path: ", save_file_path)
    # name, email = google_drive.get_user_info(access_token)
    mail.send_mail(user_name, user_email, [save_file_path])
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


# if __name__ == "__main__":
#     # process_spreadsheet("10282021_Candidates.csv", "", "", "", "")
#     process_spreadsheet("10282021_Candidates_subset.csv", "", "", "", "")
