#!/usr/bin/python3

import argparse
import json
import requests
import re

parser = argparse.ArgumentParser(description="Keep track of your NSFW games")
parser.add_argument("--list-all", help="List all games in the datebase", action="store_true")
parser.add_argument("--list-by-dev", help="List all games from a creator")
parser.add_argument("--list-by-setting", help="List all games from in a setting")
parser.add_argument("--list-by-engine", help="List all games using a certain engine")
parser.add_argument("--list-by-genre", help="List all games using in a genre")
parser.add_argument("--download", help="Download a game", action="store_true")
parser.add_argument("--os", help="The OS to download the game for")
parser.add_argument("--download-link", help="Print the download link for a game", action="store_true")
parser.add_argument("--game-name", help="The name of the game")
args = parser.parse_args()

jsonfile = open('games.json', 'r')
json_data = json.loads(jsonfile.read())

def can_download(link):
    return "mediafire.com" not in link and "mega.nz" not in link and "itch.io" not in link

def get_game_download_link(gamename, os):
    found_game = False
    for i in json_data:
        if i["game"].lower() == gamename.lower():
            found_game = True
            return i["download_link_{}".format(os)]
    if found_game == False:
        return "No game with that name found"

def get_game_download_title(r, gamename, link):
    try:
        d = r.headers['content-disposition']
        return re.findall("filename=(.+)", d)[0]
    except KeyError:
        return link.split("/")[-1:][0]

def download_game(gamename, os):
    link = get_game_download_link(gamename, os)
    # Check if we support downloading from this site
    if not can_download(link):
        print("NSFW game updater can't handle downloading from that site yet")
        print("Please download the link in your broswer")
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
            download_title = get_game_download_title(r, gamename, link)
            print("Downloading to file: {}".format(download_title))
            with open(download_title, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            print("Done")

def print_list_by(json_data, thing_to_list_by, thing_value):
    for i in json_data:
        if i[thing_to_list_by].lower() == thing_value:
            print_data(i)


def print_data(info):
    print("Developer: {dev}\nGame: {game}\nSetting: {setting}\nEngine: {engine}\nGenre: {genre}\nVisual style: {style}\n\
Animation: {animation}\nPublic Build: {public_build}\nGraphtreon: {graphtreon}\n"\
    .format(dev=info["developer"], game=info["game"], setting=info["setting"], engine=info["engine"], genre=info["genre"], \
    style=info["visual_style"], animation=info["animation"], public_build=info["public_build"], graphtreon=info["graphtreon"]))

if args.list_all:
    for i in json_data:
        print_data(i)

if args.list_by_dev:
    print_list_by(json_data, "developer", args.list_by_dev.lower())

if args.list_by_setting:
    print_list_by(json_data, "setting", args.list_by_setting.lower())

if args.list_by_engine:
    print_list_by(json_data, "engine", args.list_by_engine.lower())

if args.list_by_genre:
    print_list_by(json_data, "genre", args.list_by_genre.lower())

if args.download and args.os:
    download_game(args.game_name.lower(), args.os.lower())
elif args.download and not args.os:
    print("[!] You need to specify an OS with the --os flag")

if args.download_link:
    if args.os:
        if args.game_name:
            print("Download link: " + get_game_download_link(args.game_name.lower(), args.os.lower()))
        else:
            print("[!] You need to specify a game title with the --game-name flag")
    else:
        print("[!] You need to specify an OS with the --os flag")