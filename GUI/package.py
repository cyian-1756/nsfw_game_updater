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

excluded_files = ['config.cfg', 'log.log']
excluded_dirs = ["downloads", "install"]

def zipdir(path, ziph):
	# ziph is zipfile handle
	for root, dirs, files in os.walk(path):
		for file_ in files:
			if file_ not in excluded_files:
				ziph.write(os.path.join(root, file_))
		for dir_ in dirs:
			ziph.write(os.path.join(root, dir_))

filename = separator.join([app_name, version, platform])+".zip"
with zipfile.ZipFile(filename, 'w') as myzip:
	zipdir("dist", myzip)
