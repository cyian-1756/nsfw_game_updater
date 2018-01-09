import csv
import json

csvfile = open('games.csv', 'r')

games_list = []
fieldnames = ("developer", "game", "setting", "engine", "genre",  "visual_style", "animation", "public_build", "latest_version",\
"graphtreon", "download_link_windows", "download_link_linux", "download_link_mac", "download_link_android")
reader = csv.DictReader( csvfile, fieldnames)
for row in reader:
    # print(row)
    games_list.append(row)
t = json.dumps(games_list, jsonfile, indent=4)
print(t)
