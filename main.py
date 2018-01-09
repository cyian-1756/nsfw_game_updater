#!/usr/bin/python3

import argparse
import configparser
import datetime
import json
import sys
from hashlib import sha256
import requests

parser = argparse.ArgumentParser(description="Update your NSFW games")
parser.add_argument("--list-all", help="List all games in the datebase", action="store_true")
parser.add_argument("--list-by-dev", help="List all games from a creator")
parser.add_argument("--download-db", help="Download a copy of the DB to store locally")
args = parser.parse_args()

jsonfile = open('games.json', 'r')
json_data = json.loads(jsonfile.read())

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