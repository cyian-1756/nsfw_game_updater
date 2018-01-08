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
Animation: {animation}\nSupport: {support}\nPublic Build: {public_build}\nGraphtreon: {graphtreon}\n"\
    .format(dev=info["Developer"], game=info["Game"], setting=info["Setting"], engine=info["Engine"], genre=info["Genre"], \
    style=info["Visual style"], animation=info["Animation"], support=info["Support"], public_build=info["Public Build"], graphtreon=info["Graphtreon"]))

if args.list_all:
    for i in json_data:
        print_data(i)
if args.list_by_dev:
    for i in json_data:
        if i["Developer"].lower() == args.list_by_dev.lower():
            print_data(i)