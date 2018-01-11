import requests
import json
from bs4 import BeautifulSoup
import csv
import os
import re

jsonfile = open('games.json', 'r')
json_data = json.loads(jsonfile.read())


def get_current_download_link(game, os):
    link = ""
    for i in json_data:
        if i["game"].lower() == game.lower():
            return i["download_link_" + os]
    return None

def get_game_download_title(r):
    try:
        d = r.headers['content-disposition']
        return re.findall("filename=(.+)", d)[0]
    except KeyError:
        return None


# TODO move to using the json file
def update_csv_version(game_name, new_version):
    writer = csv.writer(open('output.csv', 'w'))
    with open('games.csv') as f:
        r = csv.reader(f)
        for line in r:
            if line[1].lower() == game_name.lower():
                line[8] = new_version
            writer.writerow(line)
    os.remove("games.csv")
    os.rename("output.csv", "games.csv")

def get_page(page):
    return requests.get(page)

def get_page_to_check(game_name):
    for i in json_data:
        if i["game"].lower() == game_name.lower():
            return i["public_build"]
    print("Could not get page")
    return None

def get_game_latest_version(game_name):
    for i in json_data:
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
        update_csv_version("insexsity", version)

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
        update_csv_version(game_name, version)
    

