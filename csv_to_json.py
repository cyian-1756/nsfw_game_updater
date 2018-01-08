import csv
import json

csvfile = open('test.csv', 'r')
jsonfile = open('file.json', 'w')

games_list = []
fieldnames = ("int", "Developer", "Game", "Setting", "Engine", "Genre",  "Visual style", "Animation", "Support", "Public Build", "Graphtreon")
reader = csv.DictReader( csvfile, fieldnames)
for row in reader:
    # print(row)
    games_list.append(row)
t = json.dumps(games_list, jsonfile, indent=4)
print(t)
