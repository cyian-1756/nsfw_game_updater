import json
import re
import os
import requests

def load_json():
    with open('games.json', 'r') as jsonfile:
        return json.loads(jsonfile.read())

def get_current_download_link(game, os):
    link = ""
    for i in load_json():
        if i["game"].lower() == game.lower():
            return i["download_link_" + os]
    return None

def update_current_download_link(game_name, os, new_link):
    # TODO rewrite this to only write the db to disk once
    json_list = []
    for sub_array in load_json():
        if sub_array["game"].lower() == game_name.lower():
            sub_array["download_link_" + os] = new_link
        json_list.append(sub_array)
    write_json_game_db(json_list)

# Check if this url was shortened
def is_shortened(url):
    return "goo.gl" in url

def unshorten_url(url):
    resp = requests.head(url, allow_redirects=True)
    return resp.url

# This checks the url and makes sure it's not shortened
def check_url(url):
    if is_shortened(url):
        print("Unshortening " + url)
        return unshorten_url(url)
    return url

def get_game_download_title(r):
    try:
        d = r.headers['content-disposition']
        return re.findall("filename=(.+)", d)[0]
    except KeyError:
        return None

def write_json_game_db(json_list):
    with open('temp_json', 'w', encoding="utf-8") as f:
         f.write(json.dumps(json_list, indent=4, sort_keys=True))
    os.remove("games.json")
    os.rename("temp_json", "games.json")

def update_json_version(game_name, new_version):
    json_list = []
    for sub_array in load_json():
        if sub_array["game"].lower() == game_name.lower():
            sub_array["latest_version"] = new_version
        json_list.append(sub_array)
    write_json_game_db(json_list)

def add_new_game(json_dict_to_add):
    if game_exists(json_dict_to_add["game"], json_dict_to_add["developer"]):
        print("Game with that title and developer is already in DB")
        return
    json_list = []
    for sub_array in load_json():
        json_list.append(sub_array)
    json_list.append(json_dict_to_add)
    write_json_game_db(json_list)

def game_exists(game_name, dev):
    for sub_array in load_json():
        if sub_array["game"].lower() == game_name.lower():
            return True
    return False

def mass_update_dev_info(dev, field, new_value):
    json_list = []
    for sub_array in load_json():
        if sub_array["developer"].lower() == dev.lower():
            sub_array[field] = new_value
        json_list.append(sub_array)
    write_json_game_db(json_list)

def update_dev_graphtreon(dev, new_graphtreon):
    mass_update_dev_info(dev, "graphtreon", new_graphtreon)
