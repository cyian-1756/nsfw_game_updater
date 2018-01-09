#!/usr/bin/python3

import argparse
import json
import requests
import re

parser = argparse.ArgumentParser(description="Update your NSFW games")
parser.add_argument("--list-all", help="List all games in the datebase", action="store_true")
parser.add_argument("--list-by-dev", help="List all games from a creator")
parser.add_argument("--download", help="Download a game")
args = parser.parse_args()

jsonfile = open('games.json', 'r')
json_data = json.loads(jsonfile.read())

def can_download(link):
    return "mediafire.com" not in link and "mega.nz" not in link

def get_game_download_link(gamename, os):
    found_game = False
    for i in json_data:
        if i["game"].lower() == gamename.lower():
            found_game = True
            return i["download_link_{}".format(os)]
    if found_game == False:
        return "No game with that name found"

def get_game_download_title(r, gamename):
    try:
        d = r.headers['content-disposition']
        return re.findall("filename=(.+)", d)[0]
    except KeyError:
        return gamename

def download_game(gamename, os):
    link = get_game_download_link(gamename, os)
    # Check if we support downloading from this site
    if not can_download(link):
        print("NSFW game updater can't handle downloading from that site yet")
        print("Please download the link in your broswer ")
        print("url: {}".format(link))
        return
    # Make sure we have the game in the database
    if link == "No game with that name found":
        print("No game with that name found")
    elif link == "Doesn’t support":
        print("Game doesn't support this OS")
    else:
        print("Download url: {}".format(link))
        print("Downloading: {}".format(link))
        r = requests.get(link, stream=True)
        if r.status_code == 200:
            print("Downloading to file: {}".format(get_game_download_title(r, gamename)))
            with open(get_game_download_title(r, gamename), 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)
            print("Done")


def print_data(info):
    print("Developer: {dev}\nGame: {game}\nSetting: {setting}\nEngine: {engine}\nGenre: {genre}\nVisual style: {style}\n\
Animation: {animation}\nPublic Build: {public_build}\nGraphtreon: {graphtreon}\n"\
    .format(dev=info["developer"], game=info["game"], setting=info["setting"], engine=info["engine"], genre=info["genre"], \
    style=info["visual_style"], animation=info["animation"], public_build=info["public_build"], graphtreon=info["graphtreon"]))

if args.list_all:
    for i in json_data:
        print_data(i)
if args.list_by_dev:
    for i in json_data:
        if i["Developer"].lower() == args.list_by_dev.lower():
            print_data(i)
if args.download:
    download_game(args.download, "windows")