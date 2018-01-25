import zipfile
from platform import system
import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("version", help="adds version to the filename", type=str)
args = parser.parse_args()

app_name = "NSFWGameManager"
separator = "-"
platform = system().lower()
version = args.version

def zipdir(path, ziph):
	# ziph is zipfile handle
	for root, dirs, files in os.walk(path):
		for file in files:
			ziph.write(os.path.join(root, file))

filename = separator.join([app_name, version, platform])+".zip"
with zipfile.ZipFile(filename, 'w') as myzip:
	zipdir("dist", myzip)
