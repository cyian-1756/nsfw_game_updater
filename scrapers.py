import requests
import json
from bs4 import BeautifulSoup
import csv
import os
import re


def load_json():
    with open('games.json', 'r') as jsonfile:
        return json.loads(jsonfile.read())

def get_current_download_link(game, os):
    link = ""
    for i in load_json():
        if i["game"].lower() == game.lower():
            return i["download_link_" + os]
    return None

def get_game_download_title(r):
    try:
        d = r.headers['content-disposition']
        return re.findall("filename=(.+)", d)[0]
    except KeyError:
        return None


def update_json_version(game_name, new_version):
    json_list = []
    for sub_array in load_json():
        if sub_array["game"].lower() == game_name.lower():
            sub_array["latest_version"] = new_version
        json_list.append(sub_array)
    with open('temp_json', 'w', encoding="utf-8") as f:
         f.write(json.dumps(json_list, indent=4))
    os.remove("games.json")
    os.rename("temp_json", "games.json")
    

def get_page(page):
    return requests.get(page)

def get_page_to_check(game_name):
    for i in load_json():
        if i["game"].lower() == game_name.lower():
            return i["public_build"]
    print("Could not get page")
    return None

def get_game_latest_version(game_name):
    for i in load_json():
        if i["game"].lower() == game_name.lower():
            return str(i["latest_version"])

def insexsity():
    r = get_page(get_page_to_check("insexsity"))
    soup = BeautifulSoup(r.text, "lxml")
    version = soup.find("div", {"class": "container-fluid"}).find("div", {"class": "warringText"}).get_text().replace("Current version- ", "")
    print("Latest version of insexsity is " + version)
    print("Latest version of insexsity in the db is " + get_game_latest_version("insexsity"))
    if str(version) != get_game_latest_version("insexsity"):
        print("There is a new version of insexsity")
        update_json_version("insexsity", version)

def trials_in_tainted_space():
    game_name = "trials in tainted space"
    link = get_current_download_link(game_name, "linux")
    if link is None:
        print("Unable to get download link for: trials in tainted space")
    r = requests.get(link, stream=True)
    version = get_game_download_title(r).replace("TiTS_", "").replace(".swf", "")
    get_game_latest_version(game_name)
    if str(version) != get_game_latest_version(game_name):
        print("There is a new version of {}".format(game_name))
        update_json_version(game_name, version)
