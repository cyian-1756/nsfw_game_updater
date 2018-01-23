import csv
import json
import sys

output = csv.writer(sys.stdout)

jsonfile = open('games.json', 'r')
json_data = json.loads(jsonfile.read())

for row in json_data:
    output.writerow(row.values())